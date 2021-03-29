CREATE DATABASE IF NOT EXISTS `university` DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci;
USE `university`;
START TRANSACTION;

drop table if exists university.university;
create table university.university(
	u_id INT NOT NULL AUTO_INCREMENT,
    u_name VARCHAR(20) NOT NULL,
    kind VARCHAR(20) NOT NULL,
    descri VARCHAR(1024),
    pdf1_path VARCHAR(256),
    pdf2_path VARCHAR(256),
    url_path VARCHAR(256),
    reward VARCHAR(10) NOT NULL,
    medal1 VARCHAR(10) NOT NULL,
    medal2 VARCHAR(10) NOT NULL,
    medal3 VARCHAR(10) NOT NULL,
    medal4 VARCHAR(10) NOT NULL,
    medal5 VARCHAR(10) NOT NULL,
    PRIMARY KEY ( u_id )
)engine=InnoDB default charset=utf8mb4 collate utf8mb4_general_ci comment='學校資訊';

COMMIT;
