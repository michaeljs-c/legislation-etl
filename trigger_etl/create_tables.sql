DROP TABLE IF EXISTS part
DROP TABLE IF EXISTS legislation_version
DROP TABLE IF EXISTS legislation
DROP TABLE IF EXISTS jurisdiction
DROP TABLE IF EXISTS issuing_body

CREATE TABLE legislation
    (
        id varchar(36) NOT NULL, 
        title varchar(255) NOT NULL, 
        native_title nvarchar(1000), 
        jurisdiction_id varchar(36) NOT NULL, 
        issuing_body_id varchar(36) NOT NULL,
        PRIMARY KEY (id)
    );

CREATE TABLE legislation_version
    (
        legislation_id varchar(36) NOT NULL,
        version_id int NOT NULL, 
        version_ordinal int NOT NULL, 
        PRIMARY KEY (legislation_id, version_ordinal),
        FOREIGN KEY (legislation_id) REFERENCES legislation(id)
    );

CREATE TABLE jurisdiction
    (
        id varchar(36) NOT NULL, 
        name varchar(255) NOT NULL,
        PRIMARY KEY (id)
    );


CREATE TABLE issuing_body
    (
        id varchar(36) NOT NULL, 
        name varchar(255) NOT NULL,
        PRIMARY KEY (id)
    );

CREATE TABLE part
    (
        id varchar(36) NOT NULL, 
        version_id int NOT NULL, 
        version_ordinal int NOT NULL, 
        legislation_id varchar(36) NOT NULL, 
        legislation_version_ordinal int NOT NULL, 
        parent_id varchar(36) NOT NULL, 
        parent_version_id int NOT NULL, 
        parent_version_ordinal int NOT NULL,
        order_num int, 
        content nvarchar(MAX),
        content_html_stipped nvarchar(MAX),
        native_content nvarchar(MAX),
        native_content_html_stripped nvarchar(MAX),
        PRIMARY KEY (id, version_ordinal),
        FOREIGN KEY (legislation_id, legislation_version_ordinal) REFERENCES legislation_version(legislation_id, version_ordinal),
        FOREIGN KEY (legislation_id) REFERENCES legislation(id)
    );
