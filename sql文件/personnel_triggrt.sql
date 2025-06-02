DELIMITER //

CREATE TRIGGER trg_after_user_insert
AFTER INSERT ON Users
FOR EACH ROW
BEGIN
    -- 校验电话号码必须为11位
    IF CHAR_LENGTH(NEW.telephoneno) != 11 THEN
        SIGNAL SQLSTATE '45000'
        SET MESSAGE_TEXT = '电话号码必须为11位';
    END IF;

    -- 根据角色插入对应表
    IF NEW.role = 'recipient' THEN
        INSERT INTO recipient(UserID, preffered_payment_methods, default_shippingaddr)
        VALUES (NEW.UserID, NULL, NULL);

    ELSEIF NEW.role = 'addresser' THEN
        INSERT INTO addresser(UserID, shippingaddr)
        VALUES (NEW.UserID, NULL);

    ELSEIF NEW.role = 'courier' THEN
        INSERT INTO courier(UserID, delivery_area)
        VALUES (NEW.UserID, NULL);
    END IF;
END //

DELIMITER ;