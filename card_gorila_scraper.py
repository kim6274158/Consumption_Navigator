"""
카드고릴라 인기순위(TOP100) 스크래퍼
실제 HTML 구조 기반으로 작성됨
JavaScript 렌더링을 위해 Playwright 사용
"""

from bs4 import BeautifulSoup
import json
import time
import csv
from datetime import datetime
from typing import List, Dict, Optional
import re

try:
    from playwright.sync_api import sync_playwright, Browser, Page
    PLAYWRIGHT_AVAILABLE = True
except ImportError:
    PLAYWRIGHT_AVAILABLE = False
    print("⚠️  Playwright가 설치되지 않았습니다. 'pip install playwright && playwright install chromium' 실행 필요")


class CardGorillaScraper:
    def __init__(self, use_playwright: bool = True):
        self.base_url = "https://www.card-gorilla.com"
        self.use_playwright = use_playwright and PLAYWRIGHT_AVAILABLE
        self.delay = 2  # 요청 간 지연시간 (초)
        self.browser: Optional[Browser] = None
        self.page: Optional[Page] = None

        if self.use_playwright:
            self.playwright = sync_playwright().start()
            self.browser = self.playwright.chromium.launch(headless=True)
            self.page = self.browser.new_page()
            self.page.set_viewport_size({"width": 1920, "height": 1080})

    def __del__(self):
        """리소스 정리"""
        if self.page:
            self.page.close()
        if self.browser:
            self.browser.close()
        if hasattr(self, 'playwright'):
            self.playwright.stop()

    def get_page(self, url: str) -> Optional[BeautifulSoup]:
        """웹페이지를 가져와서 파싱 (Playwright 사용)"""
        try:
            if not self.use_playwright:
                raise Exception("Playwright가 사용 불가능합니다. 설치가 필요합니다.")

            time.sleep(self.delay)
            self.page.goto(url, wait_until='networkidle', timeout=30000)

            # ranking_wrap이 로드될 때까지 대기
            try:
                self.page.wait_for_selector('.ranking_wrap', timeout=10000)
            except:
                # 선택자가 없어도 계속 진행
                pass

            # 추가 대기 (동적 콘텐츠 로딩)
            time.sleep(2)

            html = self.page.content()
            return BeautifulSoup(html, 'html.parser')
        except Exception as e:
            print(f"Error fetching {url}: {e}")
            return None

    def scrape_top100_cards(self, term: str = 'weekly') -> List[Dict]:
        """
        고릴라TOP100 페이지 스크래핑
        실제 HTML 구조 기반: /chart/top100?term=weekly

        Args:
            term: 기간 선택 ('weekly', 'monthly' 등)
        """
        url = f"{self.base_url}/chart/top100?term={term}"
        soup = self.get_page(url)

        if not soup:
            return []

        cards = []

        # ranking_wrap 영역 찾기
        ranking_section = soup.find('div', class_='ranking_wrap')

        if not ranking_section:
            print("Ranking section (.ranking_wrap) not found")
            return []

        # 카드 항목들 찾기 - li 태그로 구성됨
        card_items = ranking_section.find_all('li')

        if not card_items:
            # 대체 선택자 시도
            card_items = ranking_section.find_all('article') or \
                ranking_section.find_all(
                    'div', class_=re.compile('card.*item|item.*card', re.I))

        print(f"Found {len(card_items)} card items")

        for item in card_items:
            try:
                card_data = self._parse_card_item(item)
                if card_data:
                    # name이 없어도 다른 정보가 있으면 저장
                    if card_data.get('name') or card_data.get('link'):
                        cards.append(card_data)
                        rank = card_data.get('rank', '?')
                        name = card_data.get('name', card_data.get(
                            'raw_link_text', 'Unknown'))
                        print(f"Parsed card {rank}: {name[:50]}")
                    else:
                        # 디버깅: 왜 파싱이 안 되는지 확인
                        if len(cards) < 3:  # 처음 3개만 디버깅
                            print(f"Debug: Skipped item - {card_data}")
            except Exception as e:
                print(f"Error parsing card item: {e}")
                import traceback
                if len(cards) < 3:  # 처음 3개 에러만 상세 출력
                    traceback.print_exc()
                continue

        return cards

    def _parse_card_item(self, item) -> Dict:
        """
        개별 카드 항목 파싱
        실제 HTML 구조:
        - li 태그 내부
        - .num: 순위 번호
        - .updown: 순위 변동 (up/down/default)
        - a[href*="/card/detail/"]: 카드 상세 링크 및 카드명
        - img: 카드 이미지
        """
        card_data = {
            'scraped_at': datetime.now().isoformat()
        }

        # 순위 번호 (.num)
        num_elem = item.find('div', class_='num')
        if num_elem:
            rank_text = num_elem.get_text(strip=True)
            try:
                card_data['rank'] = int(rank_text)
            except ValueError:
                card_data['rank'] = rank_text

        # 순위 변동 (.updown)
        updown_elem = item.find('div', class_='updown')
        if updown_elem:
            rank_change = updown_elem.get_text(strip=True)
            card_data['rank_change'] = rank_change

            # 순위 변동 방향 (up/down/default)
            updown_classes = updown_elem.get('class', [])
            if 'up' in updown_classes:
                card_data['rank_change_direction'] = 'up'
            elif 'down' in updown_classes:
                card_data['rank_change_direction'] = 'down'
            else:
                card_data['rank_change_direction'] = 'default'

        # 카드 상세 링크 및 카드명
        # 여러 링크가 있을 수 있으므로, name_area를 포함한 링크를 찾음
        link_elem = None
        for link in item.find_all('a', href=re.compile(r'/card/detail/')):
            # name_area를 포함한 링크가 실제 카드명 링크
            if link.find('div', class_='name_area') or link.find('p', class_='card_name'):
                link_elem = link
                break

        # name_area를 포함한 링크가 없으면 첫 번째 링크 사용
        if not link_elem:
            link_elem = item.find('a', href=re.compile(r'/card/detail/'))

        if link_elem:
            href = link_elem.get('href', '')
            if href.startswith('/'):
                card_data['link'] = self.base_url + href
            elif href.startswith('http'):
                card_data['link'] = href
            else:
                card_data['link'] = self.base_url + '/' + href

            # 카드명 추출 - 여러 방법 시도
            card_name = None

            # 1. p.card_name에서 추출
            card_name_elem = link_elem.find('p', class_='card_name')
            if card_name_elem:
                card_name = card_name_elem.get_text(strip=True)

            # 2. name_area 내부의 텍스트에서 추출
            if not card_name:
                name_area = link_elem.find('div', class_='name_area')
                if name_area:
                    # name_area 내부의 모든 텍스트 수집
                    texts = [t.strip() for t in name_area.stripped_strings]
                    # 카드사명이 아닌 가장 긴 텍스트를 카드명으로 사용
                    if texts:
                        # 카드사명 제외하고 가장 긴 텍스트 선택
                        card_issuers = ['신한카드', '삼성카드', 'KB국민카드', '하나카드', '롯데카드',
                                        '현대카드', 'BC카드', 'NH카드', '우리카드', 'IBK기업은행카드',
                                        '카카오뱅크', '토스카드']
                        filtered_texts = [t for t in texts if not any(
                            issuer in t for issuer in card_issuers)]
                        if filtered_texts:
                            card_name = max(filtered_texts, key=len)
                        else:
                            card_name = max(texts, key=len)

            # 3. 링크 텍스트에서 추출 (카드사명 제외)
            if not card_name:
                link_text = link_elem.get_text(strip=True)
                if link_text:
                    # 카드사명 제거
                    card_issuers = ['신한카드', '삼성카드', 'KB국민카드', '하나카드', '롯데카드',
                                    '현대카드', 'BC카드', 'NH카드', '우리카드', 'IBK기업은행카드',
                                    '카카오뱅크', '토스카드']
                    cleaned_text = link_text
                    for issuer in card_issuers:
                        cleaned_text = cleaned_text.replace(issuer, '').strip()
                    if cleaned_text:
                        card_name = cleaned_text
                    else:
                        card_name = link_text

            # 잘못된 카드명 필터링 (페이지 제목 등)
            invalid_names = ['🏆 신용카드 실시간 인기순위', '신용카드 실시간 인기순위',
                             '인기순위', '카드고릴라', 'TOP100']
            if card_name:
                # 잘못된 값이면 None으로 설정
                if any(invalid in card_name for invalid in invalid_names):
                    card_name = None

            if card_name:
                card_data['name'] = card_name
            else:
                card_data['raw_link_text'] = link_elem.get_text(strip=True)

            # 이벤트 텍스트 (혜택 설명)
            event_elem = link_elem.find('p', class_='event_txt')
            if event_elem:
                card_data['event_text'] = event_elem.get_text(strip=True)

            # 카드사명
            corp_elem = link_elem.find('p', class_='corp_name')
            if corp_elem:
                card_data['issuer'] = corp_elem.get_text(strip=True)

        # 카드 이미지
        img_elem = item.find('img')
        if img_elem:
            src = img_elem.get('src') or img_elem.get('data-src', '')
            if src:
                if src.startswith('//'):
                    card_data['image'] = 'https:' + src
                elif src.startswith('/'):
                    card_data['image'] = self.base_url + src
                elif src.startswith('http'):
                    card_data['image'] = src
                else:
                    card_data['image'] = self.base_url + '/' + src

                # 이미지 alt 텍스트
                if img_elem.get('alt'):
                    card_data['image_alt'] = img_elem.get('alt')
                    # 카드명이 없으면 이미지 alt에서 추출 시도
                    if 'name' not in card_data or not card_data.get('name'):
                        alt_text = img_elem.get('alt', '').strip()
                        if alt_text and len(alt_text) > 2:
                            # 카드사명 제거
                            card_issuers = ['신한카드', '삼성카드', 'KB국민카드', '하나카드', '롯데카드',
                                            '현대카드', 'BC카드', 'NH카드', '우리카드', 'IBK기업은행카드',
                                            '카카오뱅크', '토스카드']
                            cleaned_alt = alt_text
                            for issuer in card_issuers:
                                cleaned_alt = cleaned_alt.replace(
                                    issuer, '').strip()
                            if cleaned_alt:
                                card_data['name'] = cleaned_alt
                            else:
                                card_data['name'] = alt_text

        # 카드사명이 아직 추출되지 않았으면 전체 텍스트에서 시도
        if 'issuer' not in card_data:
            full_text = item.get_text(strip=True)
            if full_text:
                # 카드사명 추출 시도 (일반적인 카드사명 패턴)
                card_issuers = ['신한카드', '삼성카드', 'KB국민카드', '하나카드', '롯데카드',
                                '현대카드', 'BC카드', 'NH카드', '우리카드', 'IBK기업은행카드',
                                '카카오뱅크', '토스카드']
                for issuer in card_issuers:
                    if issuer in full_text:
                        card_data['issuer'] = issuer
                        break

        return card_data

    def scrape_card_detail(self, card_url: str) -> Dict:
        """개별 카드 상세정보 스크래핑 (텍스트 설명 포함)"""
        if not self.use_playwright:
            print("⚠️  Playwright가 필요합니다. 상세정보 스크래핑을 건너뜁니다.")
            return {}

        soup = self.get_page(card_url)

        if not soup:
            return {}

        detail = {
            'url': card_url,
            'scraped_at': datetime.now().isoformat()
        }

        try:
            # 카드명 - 여러 방법 시도
            card_name = None

            # 1. h1 태그에서 추출
            title = soup.find('h1')
            if title:
                card_name = title.get_text(strip=True)

            # 2. h2 태그에서 추출 (title, name 클래스)
            if not card_name:
                title = soup.find('h2', class_=re.compile('title|name', re.I))
                if title:
                    card_name = title.get_text(strip=True)

            # 3. card_name 클래스를 가진 요소에서 추출
            if not card_name:
                name_elem = soup.find(class_=re.compile(
                    'card.*name|name.*card', re.I))
                if name_elem:
                    card_name = name_elem.get_text(strip=True)

            # 4. 상세 페이지의 제목 영역에서 추출
            if not card_name:
                title_section = soup.find(
                    'div', class_=re.compile('title|header|name', re.I))
                if title_section:
                    # h1, h2, strong 태그 찾기
                    title_tag = title_section.find(['h1', 'h2', 'strong'])
                    if title_tag:
                        card_name = title_tag.get_text(strip=True)
                    else:
                        # 첫 번째 텍스트 노드 사용
                        text = title_section.get_text(strip=True)
                        if text:
                            # 줄바꿈으로 분리하고 첫 번째 줄 사용
                            lines = [line.strip()
                                     for line in text.split('\n') if line.strip()]
                            if lines:
                                card_name = lines[0]

            # 5. 페이지 타이틀에서 추출 (fallback)
            if not card_name:
                page_title = soup.find('title')
                if page_title:
                    title_text = page_title.get_text(strip=True)
                    # "카드고릴라" 같은 사이트명 제거
                    if '카드고릴라' in title_text:
                        parts = title_text.split('카드고릴라')
                        if parts:
                            card_name = parts[0].strip()
                    else:
                        card_name = title_text

            if card_name:
                detail['name'] = card_name

            # 카드사
            issuer = soup.find(
                'span', class_=re.compile('issuer|company', re.I))
            if issuer:
                detail['issuer'] = issuer.get_text(strip=True)

            # 연회비 정보
            fee_section = soup.find('dl', class_=re.compile('fee|annual', re.I)) or \
                soup.find('div', class_=re.compile('fee|annual', re.I))
            if fee_section:
                detail['annual_fee'] = self._parse_fee_section(fee_section)

            # 혜택 정보
            benefit_section = soup.find('div', class_=re.compile('benefit', re.I)) or \
                soup.find('section', class_=re.compile('benefit', re.I))
            if benefit_section:
                detail['benefits'] = self._parse_benefits(benefit_section)

            # 카드 스펙
            spec_table = soup.find('table') or soup.find(
                'dl', class_=re.compile('spec|info', re.I))
            if spec_table:
                detail['specifications'] = self._parse_specifications(
                    spec_table)

            # 카드 설명 텍스트 수집
            detail['description_text'] = self._extract_description_text(soup)

        except Exception as e:
            print(f"Error parsing card detail: {e}")

        return detail

    def _extract_description_text(self, soup: BeautifulSoup) -> Dict:
        """카드 설명 텍스트 추출 (주요혜택, 유의사항, 연관 콘텐츠)"""
        description = {
            'benefits_text': [],
            'notices_text': [],
            'related_articles': []
        }

        try:
            # 주요혜택 섹션 찾기
            benefit_heading = soup.find('h3', string=re.compile('주요혜택'))
            if benefit_heading:
                benefit_article = benefit_heading.find_parent('article')
                if benefit_article:
                    # dt, dd 구조로 된 혜택 설명들
                    benefit_items = benefit_article.find_all(['dt', 'dd'])
                    for item in benefit_items:
                        text = item.get_text(strip=True)
                        if text and len(text) > 5 and text not in description['benefits_text']:
                            description['benefits_text'].append(text)

                    # 유의사항 텍스트 수집
                    paragraphs = benefit_article.find_all('p')
                    for p in paragraphs:
                        text = p.get_text(strip=True)
                        if text and (text.startswith('※') or text.startswith('·') or
                                     text.startswith('*') or '유의' in text or '주의' in text):
                            if text not in description['notices_text']:
                                description['notices_text'].append(text)

                    # 하단 안내 텍스트
                    notice_divs = benefit_article.find_all(
                        'div', class_=re.compile('notice|caution|warning', re.I))
                    for div in notice_divs:
                        text = div.get_text(strip=True)
                        if text and text not in description['notices_text']:
                            description['notices_text'].append(text)

            # 연관 콘텐츠 섹션 찾기
            related_heading = soup.find('h3', string=re.compile('연관'))
            if related_heading:
                related_article = related_heading.find_parent('article')
                if related_article:
                    # 연관 콘텐츠 링크들
                    related_links = related_article.find_all(
                        'a', href=re.compile(r'/contents/'))
                    for link in related_links[:5]:  # 최대 5개만
                        title_elem = link.find('p')
                        if title_elem:
                            title = title_elem.get_text(strip=True)
                            # 설명 텍스트 찾기
                            desc_elems = link.find_all(
                                'p')[1:]  # 첫 번째 p는 제목이므로 제외
                            description_text = ' '.join(
                                [p.get_text(strip=True) for p in desc_elems[:2]])

                            if title:
                                description['related_articles'].append({
                                    'title': title,
                                    'description': description_text[:500] if description_text else ''
                                })

            # 전체 설명 텍스트 합치기 (검색/요약용)
            all_text_parts = []
            all_text_parts.extend(description['benefits_text'])
            all_text_parts.extend(description['notices_text'])
            all_text_parts.extend([art.get('description', '')
                                  for art in description['related_articles']])

            description['full_description'] = ' '.join(all_text_parts)

        except Exception as e:
            print(f"Error extracting description text: {e}")

        return description

    def _parse_fee_section(self, section) -> Dict:
        """연회비 섹션 파싱"""
        fees = {}
        try:
            # dt, dd 구조
            dts = section.find_all('dt')
            dds = section.find_all('dd')
            for dt, dd in zip(dts, dds):
                key = dt.get_text(strip=True)
                value = dd.get_text(strip=True)
                fees[key] = value
        except:
            fees['raw'] = section.get_text(strip=True)
        return fees

    def _parse_benefits(self, section) -> List[Dict]:
        """혜택 섹션 파싱"""
        benefits = []
        try:
            # li 항목들
            items = section.find_all('li') or section.find_all(
                'div', class_=re.compile('item', re.I))
            for item in items:
                benefit = {}

                # 카테고리
                category = item.find(
                    'span', class_=re.compile('category|type', re.I))
                if category:
                    benefit['category'] = category.get_text(strip=True)

                # 할인율/혜택
                discount = item.find('span', class_=re.compile('discount|rate|percent', re.I)) or \
                    item.find('strong')
                if discount:
                    benefit['discount'] = discount.get_text(strip=True)

                # 설명
                desc = item.find('p') or item
                if desc:
                    benefit['description'] = desc.get_text(strip=True)

                if benefit:
                    benefits.append(benefit)
        except Exception as e:
            print(f"Error parsing benefits: {e}")
        return benefits

    def _parse_specifications(self, table) -> Dict:
        """스펙 테이블 파싱"""
        specs = {}
        try:
            if table.name == 'table':
                rows = table.find_all('tr')
                for row in rows:
                    th = row.find('th')
                    td = row.find('td')
                    if th and td:
                        specs[th.get_text(strip=True)] = td.get_text(
                            strip=True)
            else:  # dl 구조
                dts = table.find_all('dt')
                dds = table.find_all('dd')
                for dt, dd in zip(dts, dds):
                    specs[dt.get_text(strip=True)] = dd.get_text(strip=True)
        except Exception as e:
            print(f"Error parsing specs: {e}")
        return specs

    def save_to_json(self, data: List[Dict], filename: str):
        """데이터를 JSON 파일로 저장"""
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        print(f"✅ Saved {len(data)} items to {filename}")

    def save_to_csv(self, data: List[Dict], filename: str):
        """데이터를 CSV 파일로 저장"""
        if not data:
            print("No data to save")
            return

        # benefits 같은 리스트 필드를 문자열로 변환
        flattened_data = []
        for item in data:
            flat_item = item.copy()
            for key, value in flat_item.items():
                if isinstance(value, (list, dict)):
                    flat_item[key] = json.dumps(value, ensure_ascii=False)
            flattened_data.append(flat_item)

        keys = flattened_data[0].keys()
        with open(filename, 'w', newline='', encoding='utf-8-sig') as f:
            writer = csv.DictWriter(f, fieldnames=keys)
            writer.writeheader()
            writer.writerows(flattened_data)
        print(f"✅ Saved {len(data)} items to {filename}")


def main():
    """메인 실행 함수"""
    scraper = CardGorillaScraper()

    print("=" * 60)
    print("카드고릴라 TOP100 스크래핑 시작")
    print("=" * 60)

    # 1. TOP100 인기 카드 스크래핑 (주간 기준)
    print("\n[1/2] TOP100 카드 목록 스크래핑 중... (주간 기준)")
    top100_cards = scraper.scrape_top100_cards(term='weekly')

    if top100_cards:
        print(f"\n✅ 총 {len(top100_cards)}개의 카드 정보를 수집했습니다.")

        # JSON 저장
        scraper.save_to_json(top100_cards, 'cardgorilla_top100.json')

        # CSV 저장
        scraper.save_to_csv(top100_cards, 'cardgorilla_top100.csv')

        # 샘플 출력
        print("\n[샘플 데이터 미리보기]")
        print("-" * 60)
        for card in top100_cards[:3]:
            print(f"순위: {card.get('rank')}")
            print(f"카드명: {card.get('name')}")
            print(f"카드사: {card.get('issuer')}")
            print(f"연회비: {card.get('annual_fee')}")
            print(f"링크: {card.get('link')}")
            print("-" * 60)

        # 2. TOP100 전체 카드 상세정보 및 텍스트 스크래핑
        print(f"\n[2/2] TOP100 전체 카드 상세정보 및 텍스트 수집 중...")
        print(f"총 {len(top100_cards)}개 카드의 상세정보를 수집합니다. (시간이 다소 걸릴 수 있습니다)")
        detailed_cards = []
        failed_cards = []

        for idx, card in enumerate(top100_cards, 1):
            if 'link' in card and card.get('link'):
                # 카드명 추출 (여러 소스에서 시도)
                card_name = card.get('name') or card.get(
                    'image_alt') or card.get('raw_link_text') or f"카드 #{idx}"
                print(
                    f"  [{idx}/{len(top100_cards)}] {card_name} 상세정보 수집 중...", end=' ', flush=True)
                try:
                    detail = scraper.scrape_card_detail(card['link'])
                    if detail:
                        # 기본 정보와 상세정보 병합
                        merged = {**card, **detail}

                        # 카드명 우선순위: card (올바른 값) > detail > fallback
                        # 잘못된 값 필터링
                        invalid_names = ['🏆 신용카드 실시간 인기순위', '신용카드 실시간 인기순위',
                                         '인기순위', '카드고릴라', 'TOP100']

                        # 1. 기본 정보의 카드명이 올바른 값이면 우선 사용
                        card_name = card.get('name', '').strip()
                        if card_name and not any(invalid in card_name for invalid in invalid_names):
                            merged['name'] = card_name
                        # 2. 상세정보에서 추출한 카드명이 있으면 사용
                        elif detail.get('name') and detail.get('name').strip():
                            detail_name = detail.get('name').strip()
                            # 상세정보의 name도 잘못된 값이 아닌지 확인
                            if not any(invalid in detail_name for invalid in invalid_names):
                                merged['name'] = detail_name
                            else:
                                # 상세정보도 잘못된 값이면 URL에서 추출
                                url_parts = card.get('link', '').split('/')
                                if url_parts:
                                    merged['name'] = f"카드 {url_parts[-1]}"
                        # 3. 둘 다 없거나 모두 잘못된 값이면 URL에서 추출
                        else:
                            url_parts = card.get('link', '').split('/')
                            if url_parts:
                                merged['name'] = f"카드 {url_parts[-1]}"

                        detailed_cards.append(merged)
                        # 설명 텍스트가 있는지 확인
                        has_text = 'description_text' in detail and detail['description_text'].get(
                            'full_description')
                        if has_text:
                            text_len = len(detail['description_text'].get(
                                'full_description', ''))
                            print(f"✅ (텍스트: {text_len}자)")
                        else:
                            print("✅ (텍스트 없음)")
                    else:
                        print("⚠️  (상세정보 없음)")
                        # 상세정보가 없어도 기본 정보는 저장
                        detailed_cards.append(card)
                except Exception as e:
                    print(f"❌ (에러: {str(e)[:50]})")
                    failed_cards.append(
                        {'card': card_name or f"카드 #{idx}", 'error': str(e)})
                    # 에러가 발생해도 기본 정보는 저장
                    detailed_cards.append(card)
            else:
                # 링크가 없는 경우 기본 정보만 저장
                detailed_cards.append(card)

        if detailed_cards:
            scraper.save_to_json(
                detailed_cards, 'cardgorilla_top100_detailed.json')
            print(f"\n✅ 상세정보 {len(detailed_cards)}개 저장 완료")

            # 설명 텍스트가 있는 카드 수 확인
            cards_with_text = sum(1 for card in detailed_cards
                                  if card.get('description_text') and
                                  card.get('description_text', {}).get('full_description'))
            print(f"   - 설명 텍스트 포함: {cards_with_text}개")

            if failed_cards:
                print(f"\n⚠️  {len(failed_cards)}개 카드에서 에러 발생:")
                for failed in failed_cards[:5]:  # 처음 5개만 표시
                    print(f"   - {failed['card']}: {failed['error'][:50]}")

    else:
        print("\n❌ 카드 정보를 수집하지 못했습니다.")
        print("웹사이트 구조가 변경되었을 수 있습니다.")
        print("HTML 구조를 다시 확인해주세요.")

    print("\n" + "=" * 60)
    print("스크래핑 완료!")
    print("=" * 60)


if __name__ == "__main__":
    print("""
╔════════════════════════════════════════════════════════════╗
║         카드고릴라 웹 스크래퍼 v2.0                        ║
║         실제 HTML 구조 기반                                 ║
╚════════════════════════════════════════════════════════════╝

⚠️  주의사항:
1. 이 도구는 개인적인 연구/학습 목적으로만 사용하세요
2. 과도한 요청은 서버에 부담을 줄 수 있습니다
3. 수집한 데이터의 상업적 사용은 저작권 문제가 될 수 있습니다
4. robots.txt 및 이용약관을 확인하세요

시작하려면 main() 함수의 주석을 해제하세요.
    """)

    # 실행하려면 아래 주석 해제
    main()
