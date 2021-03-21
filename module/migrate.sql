CREATE DATABASE IF NOT EXISTS `vote` DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci;
USE `vote`;
START TRANSACTION;

drop table if exists vote.option;
create table vote.option(
    op_id INT NOT NULL AUTO_INCREMENT,
    op_name VARCHAR(20) NOT NULL,
    op_desc VARCHAR(80),
    op_img_path VARCHAR(100) NOT NULL,
    op_init_time date,
    op_edit_time date,
    PRIMARY KEY ( op_id )
)engine=InnoDB default charset=utf8mb4 collate utf8mb4_general_ci comment='選項';
    
   
drop table if exists vote.ballot;
create table vote.ballot(
    bal_id INT NOT NULL AUTO_INCREMENT,
    op_id INT NOT NULL,
    bal_user_id VARCHAR(20) NOT NULL,
    bal_user_name VARCHAR(50) NOT NULL,
    bal_user_message VARCHAR(100),
    PRIMARY KEY ( op_id,  bal_user_id)
)engine=InnoDB default charset=utf8mb4 collate utf8mb4_general_ci comment='選票';


COMMIT;
