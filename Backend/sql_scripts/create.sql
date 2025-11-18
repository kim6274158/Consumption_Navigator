use transaction_mockup;

-- 잔액조회 테이블
create table account_balance (
    id int primary key auto_increment,
    api_tran_id varchar(100),
    api_tran_dtm varchar(20),
    rsp_code varchar(10),
    rsp_message varchar(255),
    bank_tran_id varchar(50),
    bank_tran_date varchar(8),
    bank_code_tran varchar(10),
    bank_rsp_code varchar(10),
    bank_rsp_message varchar(255),
    bank_name varchar(100),
    savings_bank_name varchar(100),
    fintech_use_num varchar(50),
    balance_amt varchar(50),
    available_amt varchar(50),
    account_type varchar(10),
    product_name varchar(255),
    account_issue_date varchar(8),
    maturity_date varchar(8),
    last_tran_date varchar(8),
    created_at timestamp default current_timestamp
);

-- 카드기본정보조회 테이블 (기존 테이블 업데이트)
create table card_basic_info (
    id int primary key auto_increment,
    api_tran_id varchar(100),
    api_tran_dtm varchar(20),
    rsp_code varchar(10),
    rsp_message varchar(255),
    bank_tran_id varchar(50),
    bank_tran_date varchar(8),
    bank_code_tran varchar(10),
    bank_rsp_code varchar(10),
    bank_rsp_message varchar(255),
    fintech_use_num varchar(50),
    card_num varchar(50),
    card_name varchar(255),
    card_member_type varchar(10),
    card_type varchar(10),
    card_status varchar(10),
    card_issue_date varchar(8),
    card_exp_date varchar(8),
    card_brand varchar(50),
    card_corp_name varchar(100),
    corp_code varchar(10),
    created_at timestamp default current_timestamp
);

-- 카드목록조회 테이블
create table card_list (
    id int primary key auto_increment,
    api_tran_id varchar(100),
    api_tran_dtm varchar(20),
    rsp_code varchar(10),
    rsp_message varchar(255),
    bank_tran_id varchar(50),
    bank_tran_date varchar(8),
    bank_code_tran varchar(10),
    bank_rsp_code varchar(10),
    bank_rsp_message varchar(255),
    card_cnt varchar(10),
    fintech_use_num varchar(50),
    card_num varchar(50),
    card_name varchar(255),
    card_member_type varchar(10),
    card_type varchar(10),
    card_status varchar(10),
    card_issue_date varchar(8),
    card_exp_date varchar(8),
    card_brand varchar(50),
    card_corp_name varchar(100),
    created_at timestamp default current_timestamp
);