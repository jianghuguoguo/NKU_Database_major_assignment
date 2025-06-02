-- 用户表
CREATE TABLE Users (
    UserID VARCHAR(256) PRIMARY KEY,
    name VARCHAR(256),
    telephoneno VARCHAR(256),
    role VARCHAR(256)
);

-- 收件人子类表
CREATE TABLE recipient (
    UserID VARCHAR(256) PRIMARY KEY,
    preffered_payment_methods VARCHAR(256),
    default_shippingaddr VARCHAR(256),
    FOREIGN KEY (UserID) REFERENCES Users(UserID)
);

-- 发件人子类表
CREATE TABLE addresser (
    UserID VARCHAR(256) PRIMARY KEY,
    shippingaddr VARCHAR(256),
    FOREIGN KEY (UserID) REFERENCES Users(UserID)
);

-- 快递员子类表
CREATE TABLE courier (
    UserID VARCHAR(256) PRIMARY KEY,
    delivery_area VARCHAR(256),
    FOREIGN KEY (UserID) REFERENCES Users(UserID)
);

-- 订单表
CREATE TABLE `orders` (
    orderID VARCHAR(256) PRIMARY KEY,
    ostatus VARCHAR(256),
    setting_time DATETIME,
    dispatchaddr VARCHAR(256),
    reciptaddr VARCHAR(256),
    senderID VARCHAR(256),
    recipientID VARCHAR(256),
    FOREIGN KEY (senderID) REFERENCES addresser(UserID),
    FOREIGN KEY (recipientID) REFERENCES recipient(UserID)
);

-- 货物表
CREATE TABLE commodity (
    commodityID INT PRIMARY KEY,
    cstatus VARCHAR(256),
    logistic_timeline TEXT,
    Expdeliverytime DATE,
    orderID VARCHAR(256),
    courierID VARCHAR(256),
    FOREIGN KEY (orderID) REFERENCES `orders`(orderID),
    FOREIGN KEY (courierID) REFERENCES courier(UserID)
);

-- 评价表
CREATE TABLE evaluation (
    evaluationID VARCHAR(256) PRIMARY KEY,
    score VARCHAR(256),
    orderID VARCHAR(256) UNIQUE,
    recipientID VARCHAR(256),
    FOREIGN KEY (orderID) REFERENCES `orders`(orderID),
    FOREIGN KEY (recipientID) REFERENCES recipient(UserID)
);
