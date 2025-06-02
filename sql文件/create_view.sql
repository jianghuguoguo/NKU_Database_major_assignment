CREATE VIEW view_commodity_info AS
SELECT
    c.commodityID AS commodityID,
    c.cstatus AS cstatus,
    c.logistic_timeline AS logistic_timeline,
    c.Expdeliverytime AS Expdeliverytime,
    co.UserID AS courierID,
    u.name AS courier_name,
    o.orderID AS orderID,
    o.reciptaddr AS reciptaddr
FROM
    commodity c
    JOIN courier co ON c.courierID = co.UserID
    JOIN users u ON co.UserID = u.UserID
    JOIN orders o ON c.orderID = o.orderID;
