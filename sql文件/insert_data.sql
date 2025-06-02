-- 插入用户（包含三种角色）
INSERT INTO Users (UserID, name, telephoneno, role) VALUES
('U001', '张三', '13800000001', 'recipient'),
('U002', '李四', '13800000002', 'addresser'),
('U003', '王五', '13800000003', 'courier');

-- 插入子类用户
INSERT INTO recipient (UserID, preffered_payment_methods, default_shippingaddr) VALUES
('U001', '微信支付', '上海市浦东新区张江路123号');

INSERT INTO addresser (UserID, shippingaddr) VALUES
('U002', '北京市海淀区中关村南大街45号');

INSERT INTO courier (UserID, delivery_area) VALUES
('U003', '北京市全市');

-- 插入订单
INSERT INTO orders (orderID, ostatus, setting_time, dispatchaddr, reciptaddr, senderID, recipientID) VALUES
('O1001', '待揽件', '2025-05-20 10:00:00', '北京市海淀区中关村南大街45号', '上海市浦东新区张江路123号', 'U002', 'U001');

-- 插入货物信息
INSERT INTO commodity (commodityID, cstatus, logistic_timeline, Expdeliverytime, orderID, courierID) VALUES
(1, '运输中', '2025-05-20 12:00:00 已揽件；2025-05-21 08:00:00 到达分拨中心', '2025-05-23', 'O1001', 'U003');

-- 插入评价
INSERT INTO evaluation (evaluationID, score, orderID, recipientID) VALUES
('E001', '5星', 'O1001', 'U001');
