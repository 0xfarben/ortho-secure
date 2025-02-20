CREATE DATABASE IF NOT EXISTS dbortho;
USE dbortho;

CREATE TABLE IF NOT EXISTS admin (
   id  INT NOT NULL AUTO_INCREMENT,
   UserName  VARCHAR(30) DEFAULT NULL,
   Password  VARCHAR(20) DEFAULT NULL,
  PRIMARY KEY ( id )
) ENGINE=InnoDB AUTO_INCREMENT=103 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;


CREATE TABLE IF NOT EXISTS  doctors  (
   id  INT NOT NULL AUTO_INCREMENT,
   SSN  INT NOT NULL,
   FName  VARCHAR(20) DEFAULT NULL,
   MidName  VARCHAR(20) DEFAULT NULL,
   LName  VARCHAR(20) DEFAULT NULL,
   Age  INT DEFAULT NULL,
   Gender  VARCHAR(10) DEFAULT NULL,
   Phone  VARCHAR(20) DEFAULT NULL,
   Email  VARCHAR(100) DEFAULT NULL,
   Degree  VARCHAR(50) DEFAULT NULL,
   Password  VARCHAR(10) DEFAULT NULL,
   Image  VARCHAR(100) DEFAULT NULL,
  PRIMARY KEY ( id )
) ENGINE=InnoDB AUTO_INCREMENT=3 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;


CREATE TABLE IF NOT EXISTS site_information (
    Title VARCHAR(100) DEFAULT NULL,
    Address TEXT DEFAULT NULL,  -- Changed from VARCHAR(100) to TEXT
    Email VARCHAR(100) DEFAULT NULL,
    Phone VARCHAR(20) DEFAULT NULL,
    Short_description VARCHAR(500) DEFAULT NULL,
    Long_description VARCHAR(1000) DEFAULT NULL,
    Icon VARCHAR(50) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;


CREATE TABLE IF NOT EXISTS  slider  (
   ID  INT NOT NULL AUTO_INCREMENT,
   Image  VARCHAR(500) DEFAULT NULL,
   Title  VARCHAR(500) DEFAULT NULL,
   Description  VARCHAR(500) DEFAULT NULL,
  PRIMARY KEY ( ID )
) ENGINE=InnoDB AUTO_INCREMENT=4 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;


CREATE TABLE IF NOT EXISTS  treatments  (
   id  INT NOT NULL AUTO_INCREMENT,
   Image  VARCHAR(100) DEFAULT NULL,
   Name  VARCHAR(200) DEFAULT NULL,
   cost  INT DEFAULT NULL,
   Duration  INT DEFAULT NULL,
   Description  VARCHAR(500) DEFAULT NULL,
  PRIMARY KEY ( id )
) ENGINE=InnoDB AUTO_INCREMENT=3 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;


CREATE TABLE IF NOT EXISTS  users  (
   id  INT NOT NULL AUTO_INCREMENT,
   FName  VARCHAR(20) DEFAULT NULL,
   MidName  VARCHAR(20) DEFAULT NULL,
   LName  VARCHAR(20) DEFAULT NULL,
   Image  VARCHAR(100) DEFAULT NULL,
   UserName  VARCHAR(30) DEFAULT NULL,
   Password  VARCHAR(20) DEFAULT NULL,
   Email  VARCHAR(100) DEFAULT NULL,
   Phone  VARCHAR(20) DEFAULT NULL,
  PRIMARY KEY ( id )
) ENGINE=InnoDB AUTO_INCREMENT=3 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;


CREATE TABLE IF NOT EXISTS  rates  (
   Rating  INT DEFAULT NULL,
   Review  VARCHAR(500) DEFAULT NULL,
   UserID  INT DEFAULT NULL,
  KEY  UserID  ( UserID ),
  CONSTRAINT  rates_ibfk_1  FOREIGN KEY ( UserID ) REFERENCES  users  ( id )
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

CREATE TABLE IF NOT EXISTS  appointments  (
   id  INT NOT NULL AUTO_INCREMENT,
   SSN  INT NOT NULL,
   FName  VARCHAR(20) DEFAULT NULL,
   MidName  VARCHAR(20) DEFAULT NULL,
   LName  VARCHAR(20) DEFAULT NULL,
   Age  INT DEFAULT NULL,
   Gender  VARCHAR(20) DEFAULT NULL,
   Date  DATE DEFAULT NULL,
   Status  VARCHAR(20) DEFAULT NULL,
   UserID  INT NOT NULL,
   DoctorID  INT NOT NULL,
   ServiceID  INT NOT NULL,
  PRIMARY KEY ( id ),
  KEY  UserID  ( UserID ),
  KEY  DoctorID  ( DoctorID ),
  KEY  ServiceID  ( ServiceID ),
  CONSTRAINT  appointments_ibfk_1  FOREIGN KEY ( UserID ) REFERENCES  users  ( id ),
  CONSTRAINT  appointments_ibfk_2  FOREIGN KEY ( DoctorID ) REFERENCES  doctors  ( id ),
  CONSTRAINT  appointments_ibfk_3  FOREIGN KEY ( ServiceID ) REFERENCES  treatments  ( id )
) ENGINE=InnoDB AUTO_INCREMENT=9 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;


INSERT INTO  admin 
VALUES      (101,
             'Admin',
             '12345'),
            (102,
             'root',
             '12345');
UNLOCK TABLES;

INSERT INTO  users 
VALUES      (1,
             'Aarav',
             'Kapoor',
             'Singh',
             'static/img/UsersProfile/indian.jpeg',
             'ak_singh',
             '9876543210',
             'aarav.kapoor@rediff.com',
             '+919876543210'),
            (2,
             'Kiaran',
             'Sharma',
             'Bosey',
             'static/img/UsersProfile/indian1.jpeg',
             'kiara_sharma',
             '8765432190',
             'kiara.sharma@gmail.com',
             '+918765432190'),
            (3,
             'Priyank',
             'Desai',
             'Mehta',
             'static/img/UsersProfile/indian2.jpeg',
             'priya_desai',
             '7654321089',
             'priya.desai@gmail.com',
             '+917654321089'),
            (4,
             'Rohan',
             'Patel',
             'Joshi',
             'static/img/UsersProfile/indian3.jpeg',
             'rohan_patel',
             '6543210987',
             'rohan.patel@gmail.com',
             '+916543210987'),
            (5,
             'Maya',
             'Singh',
             'Kaur',
             'static/img/UsersProfile/indian4.jpg',
             'maya_kaur',
             '5432109876',
             'maya.singh@hotmail.com',
             '+915432109876');


INSERT INTO  treatments 
VALUES      (1,
             'static/img/ServicesProfile/dentistry.jpg',
             'Restorative dentistry',
             320,
             3,
'Restorative dentistry is a branch of dentistry that focuses on replacing damaged or missing teeth.'
),
            (2,
             'static/img/ServicesProfile/braces.jpg',
             'Normal Braces',
             400,
             6,
'Teeth braces are a type of orthodontic treatment that uses a variety of technologies to gradually move teeth into the desired position.\r\n'
),
            (3,
             'static/img/ServicesProfile/invisible.jpg',
             'Invisible Braces(Clean Aligners)',
             550,
             6,
'An advanced digital technology to create a series of custom-made, transparent trays that fit snugly over your teeth, applying gentle pressure to gradually shift them into the desired position.\r\n'
);


INSERT INTO  slider  VALUES      
            (1,
             'static/img/slider/img.jpg',
             'Your great smile begins with a great dentist',
             ''),
            (2,
             'static/img/slider/img2.jpg',
             'The best experience Ive ever had at my kids dentist.',
             'We happily treat patients of just about any age. Whether you are looking for a new family dentist, or just have an emergency tooth ache, we will treat you with respect and address your concerns promptly with affordable treatment options.'
            ),
            (3,
            'static/img/slider/dental_insurance_coverage_and_cost_getty_creative.jpeg',
            'Dental Health clinic',
            'Board Certified in Periodontology and Dental Implant Surgery.'
            );




INSERT INTO  doctors 
VALUES      (1,
             123456789,
             'Aarav',
             'Kapoor',
             'Singh',
             35,
             'Male',
             '9876543210',
             'aarav.kapoor@dentalclinic.com',
             'Master of Dental Surgery (MDS)',
             '1234567890',
             'static/img/doctorsProfile/doctor-1.jpg'),
            (2,
             987654321,
             'Kiara',
             'Sharma',
             'Bose',
             28,
             'Male',
             '8765432190',
             'kiara.sharma@dentalclinic.com',
             'Bachelor of Dental Surgery (BDS)',
             '0987654321',
             'static/img/doctorsProfile/doctor-2.jpg');

  
INSERT INTO  appointments 
VALUES      (1,
             123456789,
             'Arjun',
             'Kumar',
             'Singh',
             30,
             'Male',
             '2024-12-26',
             'Scheduled',
             1,
             1,
             1),
            (2,
             987654321,
             'Avani',
             'Devi',
             'Sharma',
             25,
             'Female',
             '2024-12-27',
             'Waiting',
             2,
             2,
             2)
            
            ,
            (3,
             456789123,
             'Rohan',
             'Raj',
             'Gupta',
             40,
             'Male',
             '2024-12-27',
             'Refused',
             3,
             1,
             1),
            (4,
             789123456,
             'Aditi',
             'Kumari',
             'Patel',
             35,
             'Female',
             '2024-12-28',
             'Scheduled',
             1,
             2,
             2),
            (5,
             234567890,
             'Vikram',
             'Singh',
             'Chauhan',
             50,
             'Male',
             '2024-06-27',
             'Waiting',
             2,
             1,
             1);
UNLOCK TABLES;


INSERT INTO  rates 
VALUES      
(1,'I am very satisfied with the service. The dentist was friendly and explained everything clearly.',1),
(2,
'Excellent service! The staff was very professional and the procedure was painless.',2),
(3,
'I had a great experience. The clinic is clean and the staff is very helpful.',1),
(4,'I was very nervous about my appointment, but the dentist put me at ease immediately.',2),
(5,'Highly recommend this clinic. The service was top-notch.',1);


INSERT INTO  site_information 
VALUES      ('Ortho Secure',
'KNS Institute of Technology Hegde Nagar, Kogilu Road, Yelahanka Hobli, Thirumenahalli, Bengaluru, Karnataka 560064'
             ,
'contact@orthosecure.com',
'+91 6098216430',
"every tooth in a man\'s head is more valuable than a diamond.",
"we are a group of energetic, skilled, and empathetic dental professionals who care about what’s important to you — achieving a beautiful, healthy smile for life. \r\ncombining state-of-the-art dental technology and procedures with a friendly, attentive environment, we provide a patient experience unmatched in midtown atlanta and roswell. 
\r\n
\r\nevery detail of your appointment is crafted to ensure you feel at home. enjoy our bright, lively, and comfortable office while we work hard to make your appointment effortless. 
\r\n
\r\n
our story
\r\n
\r\nat our dental, we help you celebrate the joy of a happy, healthy smile.\r\n

\r\nwe started in 2010 with the goal of reimagining the dental experience. we believe going to the dentist should be positive and empowering for the whole family, and we’re doing our part to make that the new reality. our office provides cutting-edge techniques, an experienced team, and a whole lot of time spent making sure you feel comfortable."
             ,
'static/img/icon/icon.png');