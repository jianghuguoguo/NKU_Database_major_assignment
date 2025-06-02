DELIMITER $$

CREATE PROCEDURE UpdateLogisticTimeline(
    IN in_commodityID VARCHAR(50),
    IN in_new_timeline VARCHAR(255),
    IN in_new_status VARCHAR(50)
)
BEGIN
    DECLARE curr_status VARCHAR(50);
    DECLARE v_orderID VARCHAR(50);

    -- 获取当前状态和订单号
    SELECT cstatus, orderID INTO curr_status, v_orderID
    FROM commodity
    WHERE commodityID = in_commodityID;

    -- 如果状态允许，更新时间线和状态，并同步订单状态
    IF curr_status IN ('已揽件', '运输中','订单已创建','待揽件','待派送') THEN
        UPDATE commodity
        SET logistic_timeline = in_new_timeline,
            cstatus = in_new_status
        WHERE commodityID = in_commodityID;

        UPDATE orders
        SET ostatus = in_new_status
        WHERE orderID = v_orderID;
    ELSE
        SIGNAL SQLSTATE '45000'
        SET MESSAGE_TEXT = '当前状态不允许修改物流时间线';
    END IF;
END $$
DELIMITER ;