
CREATE DATABASE UPI_FRAD_DETECTION

USE UPI_FRAD_DETECTION

--CHECKING MISSING VALUES
SELECT * FROM UPI_TRANSACTIONS
WHERE DAY_OF_WEEK IS NULL OR IS_WEEKEND  IS NULL

--- no missing value in timestamp, transaction_type, merchant_category, amount_INR, transaction_status
--- no missing value in sender_age_group, receiver_age_group, sender_state, sender_bank, receiver_bank
--- no missing value in device_type, network_type, fraud_flag, hour_of_day, day_of_week, is_weekend

--------ctrl+shift+u--------> uppercase
--------ctrl+shift+l--------> lowercase

-- 2. CHECKING FOR THE SPECIAL CHARACTER
SELECT * FROM UPI_TRANSACTIONS
WHERE AMOUNT_INR LIKE '% $%'

--3. CHECKING DUPLICATE VALUES
WITH NUM AS (
SELECT transaction_id, 
ROW_NUMBER() OVER (PARTITION BY TRANSACTION_ID ORDER BY TRANSACTION_ID) AS R
FROM UPI_TRANSACTIONS
) 
SELECT * FROM NUM
WHERE R>1

--4. Total transaction by merchant category
SELECT merchant_category,count(*) total_transaction
FROM upi_transactions
group by merchant_category

--5. Total transaction by state
select sender_state, count(*) total_transaction, 
sum(amount_inr) Total_amt
from upi_transactions
group by sender_state

--6. TOTAL FAILED TRANSACTION
select count(*) total_transaction
from upi_transactions
where transaction_status ='FAILED'

--7. TOTAL FRAUD TRANSACTION BY STATE
select sender_state, count(*) total_transaction, 
sum(amount_inr) Total_amt
from upi_transactions
WHERE FRAUD_FLAG=1
group by sender_state

--8. total fraud transaction with status is success
select sender_state, count(*) total_transaction, 
sum(amount_inr) Total_amt
from upi_transactions
WHERE FRAUD_FLAG=1 AND TRANSACTION_STATUS='SUCCESS'
group by sender_state


--
SELECT network_type,count(*) FROM UPI_TRANSACTIONS
where fraud_flag =1
group by network_type













SELECT 
    transaction_id,
    amount_INR,
    SUM(amount_INR) OVER (
        ORDER BY TIMESTAMP 
        ROWS BETWEEN 10 PRECEDING AND CURRENT ROW
    ) AS rolling_sum
FROM 
    UPI_TRANSACTIONS;

SELECT * FROM upi_transactions