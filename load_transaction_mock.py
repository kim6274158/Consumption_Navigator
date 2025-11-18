#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
transaction-mockup.json 파일의 데이터를 DB에 삽입하는 스크립트
"""
import json
import pymysql
from datetime import datetime
from typing import Optional

# DB 설정 (RDS 정보 사용)
DB_CONFIG = {
    "host": "zini-deploy.cx802ygucfor.ap-northeast-2.rds.amazonaws.com",
    "user": "admin",
    "password": "nice1234!!",
    "database": "transaction_mockup",
    "charset": "utf8mb4",
    "port": 3306,
}


def parse_datetime(tran_date: str, tran_time: str) -> datetime:
    """
    거래일자(YYYYMMDD)와 거래시간(HHMMSS)을 datetime 객체로 변환
    """
    try:
        date_str = f"{tran_date[:4]}-{tran_date[4:6]}-{tran_date[6:8]}"
        time_str = f"{tran_time[:2]}:{tran_time[2:4]}:{tran_time[4:6]}"
        return datetime.strptime(f"{date_str} {time_str}", "%Y-%m-%d %H:%M:%S")
    except Exception as e:
        print(f"날짜 변환 오류: {tran_date}, {tran_time} - {e}")
        return datetime.now()


def safe_int(value: Optional[str]) -> Optional[int]:
    """문자열을 정수로 안전하게 변환"""
    if value is None or value == "":
        return None
    try:
        return int(value)
    except (ValueError, TypeError):
        return None


def safe_bigint(value: Optional[str]) -> Optional[int]:
    """문자열을 bigint로 안전하게 변환"""
    if value is None or value == "":
        return None
    try:
        return int(value)
    except (ValueError, TypeError):
        return None


def load_transaction_mockup(json_path: str = "transaction-mockup.json"):
    """
    transaction-mockup.json 파일을 읽어서 DB에 삽입
    """
    # JSON 파일 읽기
    print(f"JSON 파일 읽는 중: {json_path}")
    with open(json_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    # DB 연결
    print("DB 연결 중...")
    conn = pymysql.connect(**DB_CONFIG)

    try:
        with conn.cursor() as cur:
            # 1. API 조회 로그 삽입 (response_success)
            response = data.get("response_success", {})
            if response:
                print("API 조회 로그 삽입 중...")

                api_inquiry_log_sql = """
                INSERT INTO api_inquiry_log (
                    api_tran_id, api_tran_dtm, rsp_code, rsp_message,
                    bank_tran_id, bank_tran_date, bank_code_tran,
                    bank_rsp_code, bank_rsp_message, bank_name,
                    savings_bank_name, fintech_use_num, balance_amt,
                    page_record_cnt, next_page_yn, befor_inquiry_trace_info
                ) VALUES (
                    %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s
                )
                """

                api_inquiry_log_values = (
                    response.get("api_tran_id"),
                    response.get("api_tran_dtm"),
                    response.get("rsp_code"),
                    response.get("rsp_message"),
                    response.get("bank_tran_id"),
                    response.get("bank_tran_date"),
                    response.get("bank_code_tran"),
                    response.get("bank_rsp_code"),
                    response.get("bank_rsp_message"),
                    response.get("bank_name"),
                    response.get("savings_bank_name"),
                    response.get("fintech_use_num"),
                    safe_bigint(response.get("balance_amt")),
                    safe_int(response.get("page_record_cnt")),
                    response.get("next_page_yn"),
                    response.get("befor_inquiry_trace_info"),
                )

                cur.execute(api_inquiry_log_sql, api_inquiry_log_values)
                api_inquiry_log_id = cur.lastrowid
                conn.commit()
                print(f"✓ API 조회 로그 삽입 완료 (ID: {api_inquiry_log_id})")
            else:
                print("⚠ response_success 데이터가 없습니다.")
                api_inquiry_log_id = None

            # 2. 거래 내역 삽입 (res_list)
            res_list = response.get("res_list", []) if response else []
            if res_list:
                print(f"거래 내역 {len(res_list)}건 삽입 중...")

                transaction_sql = """
                INSERT INTO transactions (
                    api_inquiry_log_id, fintech_use_num, tran_date, tran_time,
                    tran_datetime, inout_type, tran_type, printed_content,
                    tran_amt, after_balance_amt, branch_name
                ) VALUES (
                    %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s
                )
                """

                fintech_use_num = response.get(
                    "fintech_use_num") if response else None
                transaction_count = 0

                for transaction in res_list:
                    tran_date = transaction.get("tran_date")
                    tran_time = transaction.get("tran_time")
                    tran_datetime = parse_datetime(tran_date, tran_time)

                    transaction_values = (
                        api_inquiry_log_id,
                        fintech_use_num,
                        tran_date,
                        tran_time,
                        tran_datetime,
                        transaction.get("inout_type"),
                        transaction.get("tran_type"),
                        transaction.get("printed_content"),
                        safe_bigint(transaction.get("tran_amt")),
                        safe_bigint(transaction.get("after_balance_amt")),
                        transaction.get("branch_name"),
                    )

                    cur.execute(transaction_sql, transaction_values)
                    transaction_count += 1

                conn.commit()
                print(f"✓ 거래 내역 {transaction_count}건 삽입 완료")
            else:
                print("⚠ res_list 데이터가 없습니다.")

            # 3. API 요청 파라미터 로그 삽입 (request.parameters)
            request_params = data.get("request", {}).get("parameters", {})
            if request_params and api_inquiry_log_id:
                print("API 요청 파라미터 로그 삽입 중...")

                api_request_log_sql = """
                INSERT INTO api_request_log (
                    api_inquiry_log_id, bank_tran_id, fintech_use_num,
                    inquiry_type, inquiry_base, from_date, from_time,
                    to_date, to_time, sort_order, tran_dtime,
                    befor_inquiry_trace_info
                ) VALUES (
                    %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s
                )
                """

                api_request_log_values = (
                    api_inquiry_log_id,
                    request_params.get("bank_tran_id"),
                    request_params.get("fintech_use_num"),
                    request_params.get("inquiry_type"),
                    request_params.get("inquiry_base"),
                    request_params.get("from_date"),
                    request_params.get("from_time"),
                    request_params.get("to_date"),
                    request_params.get("to_time"),
                    request_params.get("sort_order"),
                    request_params.get("tran_dtime"),
                    request_params.get("befor_inquiry_trace_info"),
                )

                cur.execute(api_request_log_sql, api_request_log_values)
                conn.commit()
                print("✓ API 요청 파라미터 로그 삽입 완료")
            else:
                print("⚠ API 요청 파라미터 데이터가 없거나 API 조회 로그 ID가 없습니다.")

        print("\n✅ 모든 데이터 삽입 완료!")

    except Exception as e:
        conn.rollback()
        print(f"\n❌ 오류 발생: {e}")
        import traceback
        traceback.print_exc()
        raise
    finally:
        conn.close()
        print("DB 연결 종료")


def main():
    """메인 함수"""
    import sys

    # 커맨드라인 인자로 JSON 파일 경로를 받을 수 있음
    json_path = sys.argv[1] if len(sys.argv) > 1 else "transaction-mockup.json"

    # DB 설정을 환경변수나 커맨드라인에서 받을 수 있도록 확장 가능
    # 예: DB_CONFIG["host"] = os.getenv("DB_HOST", "localhost")

    try:
        load_transaction_mockup(json_path)
    except FileNotFoundError:
        print(f"❌ 파일을 찾을 수 없습니다: {json_path}")
        sys.exit(1)
    except pymysql.Error as e:
        print(f"❌ DB 오류: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"❌ 예상치 못한 오류: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
