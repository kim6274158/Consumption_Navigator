#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
잔액조회, 카드기본정보조회, 카드목록조회 JSON 파일의 데이터를 DB에 삽입하는 스크립트
"""
import json
import pymysql
import sys
from typing import Optional

# DB 설정
DB_CONFIG = {
    "host": "zini-deploy.cx802ygucfor.ap-northeast-2.rds.amazonaws.com",
    "user": "admin",
    "password": "nice1234!!",
    "database": "transaction_mockup",
    "charset": "utf8mb4",
    "port": 3306,
}


def load_account_balance(json_path: str = "mockup_data/잔액조회.json"):
    """
    잔액조회.json 파일을 읽어서 account_balance 테이블에 삽입
    """
    print(f"\n{'='*60}")
    print(f"잔액조회 데이터 로드 시작: {json_path}")
    print(f"{'='*60}")

    # JSON 파일 읽기
    with open(json_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    # DB 연결
    conn = pymysql.connect(**DB_CONFIG)

    try:
        with conn.cursor() as cur:
            # response_success_examples 배열 처리
            success_examples = data.get("response_success_examples", [])

            if not success_examples:
                print("⚠ response_success_examples 데이터가 없습니다.")
                return

            print(f"잔액조회 예시 {len(success_examples)}건 처리 중...")

            sql = """
            INSERT INTO account_balance (
                api_tran_id, api_tran_dtm, rsp_code, rsp_message,
                bank_tran_id, bank_tran_date, bank_code_tran,
                bank_rsp_code, bank_rsp_message, bank_name,
                savings_bank_name, fintech_use_num, balance_amt,
                available_amt, account_type, product_name,
                account_issue_date, maturity_date, last_tran_date
            ) VALUES (
                %s, %s, %s, %s, %s, %s, %s, %s, %s, %s,
                %s, %s, %s, %s, %s, %s, %s, %s, %s
            )
            """

            count = 0
            for example in success_examples:
                account_data = example.get("data", {})
                if not account_data:
                    continue

                values = (
                    account_data.get("api_tran_id"),
                    account_data.get("api_tran_dtm"),
                    account_data.get("rsp_code"),
                    account_data.get("rsp_message"),
                    account_data.get("bank_tran_id"),
                    account_data.get("bank_tran_date"),
                    account_data.get("bank_code_tran"),
                    account_data.get("bank_rsp_code"),
                    account_data.get("bank_rsp_message"),
                    account_data.get("bank_name"),
                    account_data.get("savings_bank_name"),
                    account_data.get("fintech_use_num"),
                    account_data.get("balance_amt"),
                    account_data.get("available_amt"),
                    account_data.get("account_type"),
                    account_data.get("product_name"),
                    account_data.get("account_issue_date"),
                    account_data.get("maturity_date") or None,
                    account_data.get("last_tran_date"),
                )

                cur.execute(sql, values)
                count += 1
                print(f"  ✓ {example.get('description', 'N/A')} 삽입 완료")

            conn.commit()
            print(f"\n✅ 잔액조회 데이터 {count}건 삽입 완료!")

    except Exception as e:
        conn.rollback()
        print(f"\n❌ 오류 발생: {e}")
        import traceback
        traceback.print_exc()
        raise
    finally:
        conn.close()


def load_card_basic_info(json_path: str = "mockup_data/카드기본정보조회.json"):
    """
    카드기본정보조회.json 파일을 읽어서 card_basic_info 테이블에 삽입
    """
    print(f"\n{'='*60}")
    print(f"카드기본정보조회 데이터 로드 시작: {json_path}")
    print(f"{'='*60}")

    # JSON 파일 읽기
    with open(json_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    # DB 연결
    conn = pymysql.connect(**DB_CONFIG)

    try:
        with conn.cursor() as cur:
            sql = """
            INSERT INTO card_basic_info (
                api_tran_id, api_tran_dtm, rsp_code, rsp_message,
                bank_tran_id, bank_tran_date, bank_code_tran,
                bank_rsp_code, bank_rsp_message, fintech_use_num,
                card_num, card_name, card_member_type, card_type,
                card_status, card_issue_date, card_exp_date,
                card_brand, card_corp_name, corp_code
            ) VALUES (
                %s, %s, %s, %s, %s, %s, %s, %s, %s, %s,
                %s, %s, %s, %s, %s, %s, %s, %s, %s, %s
            )
            """

            values = (
                data.get("api_tran_id"),
                data.get("api_tran_dtm"),
                data.get("rsp_code"),
                data.get("rsp_message"),
                data.get("bank_tran_id"),
                data.get("bank_tran_date"),
                data.get("bank_code_tran"),
                data.get("bank_rsp_code"),
                data.get("bank_rsp_message"),
                data.get("fintech_use_num"),
                data.get("card_num"),
                data.get("card_name"),
                data.get("card_member_type"),
                data.get("card_type"),
                data.get("card_status"),
                data.get("card_issue_date"),
                data.get("card_exp_date"),
                data.get("card_brand"),
                data.get("card_corp_name"),
                data.get("corp_code"),
            )

            cur.execute(sql, values)
            conn.commit()
            print(f"✅ 카드기본정보조회 데이터 삽입 완료!")
            print(f"  - 카드명: {data.get('card_name')}")
            print(f"  - 카드번호: {data.get('card_num')}")

    except Exception as e:
        conn.rollback()
        print(f"\n❌ 오류 발생: {e}")
        import traceback
        traceback.print_exc()
        raise
    finally:
        conn.close()


def load_card_list(json_path: str = "mockup_data/카드목록조회.json"):
    """
    카드목록조회.json 파일을 읽어서 card_list 테이블에 삽입
    """
    print(f"\n{'='*60}")
    print(f"카드목록조회 데이터 로드 시작: {json_path}")
    print(f"{'='*60}")

    # JSON 파일 읽기
    with open(json_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    # DB 연결
    conn = pymysql.connect(**DB_CONFIG)

    try:
        with conn.cursor() as cur:
            # card_list 배열의 각 항목마다 레코드 생성
            card_list = data.get("card_list", [])

            if not card_list:
                print("⚠ card_list 데이터가 없습니다.")
                return

            print(f"카드 목록 {len(card_list)}건 처리 중...")

            sql = """
            INSERT INTO card_list (
                api_tran_id, api_tran_dtm, rsp_code, rsp_message,
                bank_tran_id, bank_tran_date, bank_code_tran,
                bank_rsp_code, bank_rsp_message, card_cnt,
                fintech_use_num, card_num, card_name, card_member_type,
                card_type, card_status, card_issue_date, card_exp_date,
                card_brand, card_corp_name
            ) VALUES (
                %s, %s, %s, %s, %s, %s, %s, %s, %s, %s,
                %s, %s, %s, %s, %s, %s, %s, %s, %s, %s
            )
            """

            count = 0
            for card in card_list:
                values = (
                    data.get("api_tran_id"),  # 상위 레벨의 공통 필드
                    data.get("api_tran_dtm"),
                    data.get("rsp_code"),
                    data.get("rsp_message"),
                    data.get("bank_tran_id"),
                    data.get("bank_tran_date"),
                    data.get("bank_code_tran"),
                    data.get("bank_rsp_code"),
                    data.get("bank_rsp_message"),
                    data.get("card_cnt"),
                    card.get("fintech_use_num"),
                    card.get("card_num"),
                    card.get("card_name"),
                    card.get("card_member_type"),
                    card.get("card_type"),
                    card.get("card_status"),
                    card.get("card_issue_date"),
                    card.get("card_exp_date"),
                    card.get("card_brand"),
                    card.get("card_corp_name"),
                )

                cur.execute(sql, values)
                count += 1
                print(f"  ✓ {card.get('card_name', 'N/A')} 삽입 완료")

            conn.commit()
            print(f"\n✅ 카드목록조회 데이터 {count}건 삽입 완료!")

    except Exception as e:
        conn.rollback()
        print(f"\n❌ 오류 발생: {e}")
        import traceback
        traceback.print_exc()
        raise
    finally:
        conn.close()


def main():
    """메인 함수"""
    import argparse

    parser = argparse.ArgumentParser(description="JSON 모킹 데이터를 DB에 로드")
    parser.add_argument(
        "--account-balance",
        action="store_true",
        help="잔액조회 데이터 로드"
    )
    parser.add_argument(
        "--card-basic-info",
        action="store_true",
        help="카드기본정보조회 데이터 로드"
    )
    parser.add_argument(
        "--card-list",
        action="store_true",
        help="카드목록조회 데이터 로드"
    )
    parser.add_argument(
        "--all",
        action="store_true",
        help="모든 데이터 로드"
    )

    args = parser.parse_args()

    try:
        if args.all or (not args.account_balance and not args.card_basic_info and not args.card_list):
            # 인자가 없으면 모두 실행
            load_account_balance()
            load_card_basic_info()
            load_card_list()
        else:
            if args.account_balance:
                load_account_balance()
            if args.card_basic_info:
                load_card_basic_info()
            if args.card_list:
                load_card_list()

        print(f"\n{'='*60}")
        print("✅ 모든 작업 완료!")
        print(f"{'='*60}\n")

    except FileNotFoundError as e:
        print(f"❌ 파일을 찾을 수 없습니다: {e}")
        sys.exit(1)
    except pymysql.Error as e:
        print(f"❌ DB 오류: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"❌ 예상치 못한 오류: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
