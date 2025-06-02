DELIMITER //

CREATE TRIGGER set_order_time
BEFORE INSERT ON orders
FOR EACH ROW
BEGIN
    SET NEW.setting_time = NOW();
END;
//

DELIMITER ;
