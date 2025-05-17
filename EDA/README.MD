## About Dataset
DATA -  IEEE-CIS Fraud Detection from KAGGLE
Transaction data

Transaction id: Id related to the transaction
TransactionDT: timedelta from a given reference datetime (not an actual timestamp)
TransactionAMT: transaction payment amount in USD
ProductCD [Categorical]: product code(the product for each transaction)
card1–6 [Categorical]: payment card related information like card type, country etc
addr1, addr2 [Categorical]: address information
dist1,dist2: some distance information
_P_emaildomain [Categorical]: email domain of purchaser._
_R_emaildomain [Categorical]: email domain of the recipient._
C1-C14: counting, such as how many addresses are found to be associated with the payment card, etc. The actual meaning is masked.
D1-D15: time delta, such as days between the previous transactions, etc.
M1-M9 [Categorical]: match, such as names on card and address, etc.
Vxxx: Vesta engineered rich features, including ranking, counting, and other entity relations.
Identity data

Transaction id: Id related to the transaction
DeviceType [Categorical]: Type of device used for the transaction
DeviceInfo [Categorical]: More information about device used
id 1–38 [Categorical+numeric]: network connection information,browser information etc (id 12–38 are categorical information)
