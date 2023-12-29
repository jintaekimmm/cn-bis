CREATE TABLE IF NOT EXISTS bus_route
(
    id           bigint primary key auto_increment,
    route_id     bigint       not null comment '노선 ID',
    route_name   varchar(32)  not null comment '노선명',
    route_order  int          not null comment '노선 순번',
    node_id      bigint       not null comment 'Node Id',
    ars_id       bigint       not null comment 'ARS ID',
    station_name varchar(255) not null comment '정류소 이름',
    location     point        not null SRID 4326 comment '정류소 위치',
    created_at   datetime(6)  not null comment '생성일자',
    updated_at   datetime(6)  not null comment '변경일자'
);

CREATE INDEX idx_route_name
    ON bus_route (route_name);
CREATE INDEX ars_id
    ON bus_route (ars_id);
CREATE INDEX idx_station_name
    ON bus_route (station_name);
CREATE SPATIAL INDEX spx_location
    ON bus_route (location);

CREATE TABLE IF NOT EXISTS bus_station
(
    id            bigint primary key auto_increment,
    node_id       varchar(64)  not null comment '정류장 ID',
    node_name     varchar(128) not null comment '정류장 이름',
    location      point        not null SRID 4326 not null comment '정류장 위치',
    collectd_time date         not null comment '정보 수집일',
    mobile_id     bigint       not null comment '모바일 단축번호',
    city_code     bigint       not null comment '도시 코드',
    city_name     varchar(16)  not null comment '도시명',
    admin_name    varchar(16)  not null comment '관리 도시명',
    created_at    datetime(6)  not null comment '생성일자',
    updated_at    datetime(6)  not null comment '변경일자'
);

CREATE INDEX idx_node_name
    ON bus_station (node_name);
CREATE INDEX idx_mobile_id
    ON bus_station (mobile_id);
CREATE SPATIAL INDEX spx_location
    ON bus_station (location);


CREATE TABLE IF NOT EXISTS hang_jeong_gu
(
    id           bigint primary key auto_increment,
    sig_code     int         not null comment '시구 코드',
    sido         varchar(32) not null comment '시도 이름',
    sig_eng_name varchar(64) not null comment '시구 영어 이름',
    sig_kor_name varchar(64) not null comment '시구 한글 이름',
    geometry     POLYGON     SRID 4326 not null comment '위치(Polygon)',
    created_at   datetime(6) not null comment '생성일자',
    updated_at   datetime(6) not null comment '변경일자'
);

CREATE INDEX idx_sig_kor_name
    ON hang_jeong_gu (sig_kor_name);

CREATE SPATIAL INDEX spx_geometry
    ON hang_jeong_gu (geometry);
