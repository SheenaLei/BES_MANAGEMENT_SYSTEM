-- Sample data for residents table - 100 RESIDENTS
-- Run this after creating the residents table

INSERT INTO residents (
    last_name, first_name, middle_name, suffix,
    gender, birth_date, birth_place, age, civil_status,
    spouse_name, no_of_children, no_of_siblings,
    mother_full_name, father_full_name,
    nationality, religion, occupation, highest_educational_attainment,
    contact_number, emergency_contact_name, emergency_contact_number,
    sitio, barangay, municipality,
    registered_voter, indigent, solo_parent, solo_parent_id_no, fourps_member
) VALUES

-- PANDAYAN, APLAYA, CENTRO RESIDENTS (40 people)
-- Family Santos
('Santos', 'Juan', 'Cruz', NULL, 'Male', '1985-03-15', 'Manila', 38, 'Married', 'Maria Santos', 3, 2, 'Rosa Cruz', 'Pedro Santos', 'Filipino', 'Roman Catholic', 'Tricycle Driver', 'High School Graduate', '09171234567', 'Maria Santos', '09171234568', 'Pandayan', 'Barangay Balibago', 'Calatagan', TRUE, FALSE, FALSE, NULL, TRUE),
('Santos', 'Maria', 'Reyes', NULL, 'Female', '1987-07-22', 'Batangas', 36, 'Married', 'Juan Santos', 3, 3, 'Carmen Reyes', 'Jose Reyes', 'Filipino', 'Roman Catholic', 'Housewife', 'College Level', '09171234568', 'Juan Santos', '09171234567', 'Aplaya', 'Barangay Balibago', 'Calatagan', TRUE, FALSE, FALSE, NULL, TRUE),
('Santos', 'Jose', 'Cruz', NULL, 'Male', '2010-05-10', 'Calatagan', 13, 'Single', NULL, 0, 2, 'Maria Santos', 'Juan Santos', 'Filipino', 'Roman Catholic', 'Student', 'Elementary Level', '09171234567', 'Maria Santos', '09171234568', 'Centro', 'Barangay Balibago', 'Calatagan', FALSE, FALSE, FALSE, NULL, TRUE),

-- Family Garcia
('Garcia', 'Ana', 'Lopez', NULL, 'Female', '1995-05-30', 'Lipa City', 28, 'Single', NULL, 1, 1, 'Elena Lopez', 'Miguel Lopez', 'Filipino', 'Roman Catholic', 'Vendor', 'High School Graduate', '09193456789', 'Elena Garcia', '09193456780', 'Pandayan', 'Barangay Balibago', 'Calatagan', TRUE, TRUE, TRUE, 'SP-2023-001', TRUE),
('Garcia', 'Mark', 'Lopez', NULL, 'Male', '2019-08-15', 'Calatagan', 4, 'Single', NULL, 0, 0, 'Ana Garcia', 'Unknown', 'Filipino', 'Roman Catholic', 'None', 'Pre-school', '09193456789', 'Ana Garcia', '09193456780', 'Aplaya', 'Barangay Balibago', 'Calatagan', FALSE, TRUE, FALSE, NULL, TRUE),

-- Family Torres
('Torres', 'Liza', 'Mercado', NULL, 'Female', '1982-06-11', 'Taal', 41, 'Widowed', NULL, 2, 3, 'Rosa Mercado', 'Carlos Mercado', 'Filipino', 'Roman Catholic', 'Sari-sari Store Owner', 'High School Graduate', '09226789012', 'Rosa Torres', '09226789013', 'Centro', 'Barangay Balibago', 'Calatagan', TRUE, TRUE, TRUE, 'SP-2022-045', TRUE),
('Torres', 'Jenny', 'Mercado', NULL, 'Female', '2005-02-20', 'Calatagan', 18, 'Single', NULL, 0, 1, 'Liza Torres', 'Roberto Torres', 'Filipino', 'Roman Catholic', 'Student', 'Senior High', '09226789012', 'Liza Torres', '09226789013', 'Pandayan', 'Barangay Balibago', 'Calatagan', TRUE, TRUE, FALSE, NULL, TRUE),
('Torres', 'Roy', 'Mercado', NULL, 'Male', '2008-11-05', 'Calatagan', 15, 'Single', NULL, 0, 1, 'Liza Torres', 'Roberto Torres', 'Filipino', 'Roman Catholic', 'Student', 'Junior High', '09226789012', 'Liza Torres', '09226789013', 'Aplaya', 'Barangay Balibago', 'Calatagan', FALSE, TRUE, FALSE, NULL, TRUE),

-- Family Aquino
('Aquino', 'Benjamin', 'Castillo', NULL, 'Male', '1992-01-19', 'Calatagan', 31, 'Married', 'Jennifer Aquino', 2, 3, 'Nilda Castillo', 'Ramon Castillo', 'Filipino', 'Roman Catholic', 'Farmer', 'Elementary Graduate', '09259012345', 'Jennifer Aquino', '09259012346', 'Centro', 'Barangay Balibago', 'Calatagan', TRUE, TRUE, FALSE, NULL, TRUE),
('Aquino', 'Jennifer', 'Ocampo', NULL, 'Female', '1994-08-03', 'Lipa', 29, 'Married', 'Benjamin Aquino', 2, 2, 'Luz Ocampo', 'Ricardo Ocampo', 'Filipino', 'Roman Catholic', 'Housewife', 'High School Graduate', '09259012346', 'Benjamin Aquino', '09259012345', 'Pandayan', 'Barangay Balibago', 'Calatagan', TRUE, TRUE, FALSE, NULL, TRUE),
('Aquino', 'Bryan', 'Ocampo', NULL, 'Male', '2015-03-12', 'Calatagan', 8, 'Single', NULL, 0, 1, 'Jennifer Aquino', 'Benjamin Aquino', 'Filipino', 'Roman Catholic', 'Student', 'Elementary Level', '09259012346', 'Jennifer Aquino', '09259012345', 'Aplaya', 'Barangay Balibago', 'Calatagan', FALSE, TRUE, FALSE, NULL, TRUE),
('Aquino', 'Baby Girl', 'Ocampo', NULL, 'Female', '2020-09-25', 'Calatagan', 3, 'Single', NULL, 0, 1, 'Jennifer Aquino', 'Benjamin Aquino', 'Filipino', 'Roman Catholic', 'None', 'Pre-school', '09259012346', 'Jennifer Aquino', '09259012345', 'Centro', 'Barangay Balibago', 'Calatagan', FALSE, TRUE, FALSE, NULL, TRUE),

-- Seniors in Sitio 1
('Velasco', 'Remedios', 'Santos', NULL, 'Female', '1950-12-10', 'Batangas', 73, 'Widowed', NULL, 6, 5, 'Felicidad Santos', 'Vicente Santos', 'Filipino', 'Roman Catholic', 'Retired', 'Elementary Graduate', '09271234567', 'Ana Garcia', '09193456789', 'Pandayan', 'Barangay Balibago', 'Calatagan', TRUE, TRUE, FALSE, NULL, FALSE),
('Cruz', 'Teresita', 'Villanueva', NULL, 'Female', '1958-04-15', 'Manila', 65, 'Widowed', NULL, 4, 3, 'Maria Villanueva', 'Jose Villanueva', 'Filipino', 'Roman Catholic', 'Retired Teacher', 'College Graduate', '09281234567', 'Liza Torres', '09226789012', 'Aplaya', 'Barangay Balibago', 'Calatagan', TRUE, FALSE, FALSE, NULL, FALSE),

-- Young Families Sitio 1
('Tan', 'Sarah', 'Lim', NULL, 'Female', '2002-05-12', 'Manila', 21, 'Single', NULL, 0, 1, 'Grace Lim', 'Michael Lim', 'Filipino', 'Christian', 'College Student', 'College Level', '09304567890', 'Grace Tan', '09304567891', 'Centro', 'Barangay Balibago', 'Calatagan', FALSE, FALSE, FALSE, NULL, FALSE),
('Mendoza', 'Carlo', 'Diaz', NULL, 'Male', '1996-09-20', 'Tanauan', 27, 'Married', 'Kaye Mendoza', 1, 2, 'Linda Diaz', 'Mario Diaz', 'Filipino', 'Roman Catholic', 'Security Guard', 'High School Graduate', '09315678901', 'Kaye Mendoza', '09315678902', 'Pandayan', 'Barangay Balibago', 'Calatagan', TRUE, FALSE, FALSE, NULL, FALSE),
('Mendoza', 'Kaye', 'Pascual', NULL, 'Female', '1998-12-08', 'Batangas', 25, 'Married', 'Carlo Mendoza', 1, 1, 'Anna Pascual', 'Ben Pascual', 'Filipino', 'Roman Catholic', 'Online Seller', 'College Level', '09315678902', 'Carlo Mendoza', '09315678901', 'Aplaya', 'Barangay Balibago', 'Calatagan', TRUE, FALSE, FALSE, NULL, FALSE),

-- More Sitio 1 Residents
('Rivera', 'Gloria', 'Valdez', NULL, 'Female', '1980-07-30', 'Calatagan', 43, 'Single', NULL, 2, 4, 'Nora Valdez', 'Ramon Valdez', 'Filipino', 'Iglesia ni Cristo', 'Laundrywoman', 'Elementary Graduate', '09326789012', 'Nora Rivera', '09326789013', 'Centro', 'Barangay Balibago', 'Calatagan', TRUE, TRUE, TRUE, 'SP-2021-089', TRUE),
('Lopez', 'Eddie', 'Gomez', NULL, 'Male', '1975-11-22', 'Manila', 48, 'Married', 'Celia Lopez', 3, 2, 'Rosa Gomez', 'Ernesto Gomez', 'Filipino', 'Roman Catholic', 'Carpenter', 'Vocational Graduate', '09337890123', 'Celia Lopez', '09337890124', 'Pandayan', 'Barangay Balibago', 'Calatagan', TRUE, FALSE, FALSE, NULL, FALSE),
('Lopez', 'Celia', 'Ruiz', NULL, 'Female', '1977-02-14', 'Lipa', 46, 'Married', 'Eddie Lopez', 3, 3, 'Carmen Ruiz', 'Pablo Ruiz', 'Filipino', 'Roman Catholic', 'Manicurist', 'High School Graduate', '09337890124', 'Eddie Lopez', '09337890123', 'Aplaya', 'Barangay Balibago', 'Calatagan', TRUE, FALSE, FALSE, NULL, FALSE),
('Bautista', 'Ramon', 'Del Rosario', NULL, 'Male', '1990-06-18', 'Batangas City', 33, 'Live-in', 'Annabel Bautista', 2, 1, 'Teresa Del Rosario', 'Carlos Del Rosario', 'Filipino', 'Born Again', 'Delivery Rider', 'High School Graduate', '09348901234', 'Annabel Bautista', '09348901235', 'Centro', 'Barangay Balibago', 'Calatagan', TRUE, TRUE, FALSE, NULL, TRUE),
('Bautista', 'Annabel', 'Flores', NULL, 'Female', '1992-03-25', 'Calatagan', 31, 'Live-in', 'Ramon Bautista', 2, 2, 'Gina Flores', 'Tony Flores', 'Filipino', 'Born Again', 'Housewife', 'High School Graduate', '09348901235', 'Ramon Bautista', '09348901234', 'Pandayan', 'Barangay Balibago', 'Calatagan', TRUE, TRUE, FALSE, NULL, TRUE),
('Reyes', 'Angela', 'De Guzman', NULL, 'Female', '1988-10-05', 'Taal', 35, 'Separated', NULL, 1, 3, 'Nena De Guzman', 'Romy De Guzman', 'Filipino', 'Roman Catholic', 'Factory Worker', 'High School Graduate', '09359012345', 'Nena Reyes', '09359012346', 'Aplaya', 'Barangay Balibago', 'Calatagan', TRUE, TRUE, TRUE, 'SP-2020-112', TRUE),
('Navarro', 'Richard', 'Santos', NULL, 'Male', '2000-01-10', 'Manila', 23, 'Single', NULL, 0, 2, 'Linda Santos', 'Rico Santos', 'Filipino', 'Roman Catholic', 'Construction Worker', 'High School Graduate', '09360123456', 'Linda Navarro', '09360123457', 'Centro', 'Barangay Balibago', 'Calatagan', TRUE, FALSE, FALSE, NULL, FALSE),
('Santiago', 'Princess', 'Alvarez', NULL, 'Female', '2003-07-22', 'Calatagan', 20, 'Single', NULL, 0, 3, 'Mely Alvarez', 'Pete Alvarez', 'Filipino', 'Roman Catholic', 'Cashier', 'Senior High Graduate', '09371234567', 'Mely Santiago', '09371234568', 'Pandayan', 'Barangay Balibago', 'Calatagan', TRUE, FALSE, FALSE, NULL, FALSE),
('Castillo', 'Dennis', 'Mercado', NULL, 'Male', '1983-12-30', 'Lipa', 40, 'Divorced', NULL, 1, 1, 'Rosie Mercado', 'Danny Mercado', 'Filipino', 'Iglesia ni Cristo', 'Jeepney Driver', 'Elementary Graduate', '09382345678', 'Rosie Castillo', '09382345679', 'Aplaya', 'Barangay Balibago', 'Calatagan', TRUE, TRUE, FALSE, NULL, FALSE),

-- DITA, TULAY NA BATO RESIDENTS (35 people)
-- Family Ramos
('Ramos', 'Roberto', 'Mendoza', NULL, 'Male', '1978-12-25', 'Manila', 45, 'Married', 'Cristina Ramos', 5, 3, 'Rosario Mendoza', 'Antonio Mendoza', 'Filipino', 'Born Again Christian', 'Construction Worker', 'College Graduate', '09204567890', 'Cristina Ramos', '09204567891', 'Dita', 'Barangay Balibago', 'Calatagan', TRUE, FALSE, FALSE, NULL, FALSE),
('Ramos', 'Cristina', 'Bautista', NULL, 'Female', '1980-09-14', 'Batangas', 43, 'Married', 'Roberto Ramos', 5, 2, 'Maria Bautista', 'Juan Bautista', 'Filipino', 'Born Again Christian', 'Teacher', 'College Graduate', '09204567891', 'Roberto Ramos', '09204567890', 'Tulay na Bato', 'Barangay Balibago', 'Calatagan', TRUE, FALSE, FALSE, NULL, FALSE),
('Ramos', 'Michael', 'Bautista', NULL, 'Male', '2005-04-10', 'Calatagan', 18, 'Single', NULL, 0, 4, 'Cristina Ramos', 'Roberto Ramos', 'Filipino', 'Born Again Christian', 'Student', 'Senior High', '09204567891', 'Cristina Ramos', '09204567890', 'Dita', 'Barangay Balibago', 'Calatagan', TRUE, FALSE, FALSE, NULL, FALSE),
('Ramos', 'Christine', 'Bautista', NULL, 'Female', '2007-08-22', 'Calatagan', 16, 'Single', NULL, 0, 4, 'Cristina Ramos', 'Roberto Ramos', 'Filipino', 'Born Again Christian', 'Student', 'Junior High', '09204567891', 'Cristina Ramos', '09204567890', 'Tulay na Bato', 'Barangay Balibago', 'Calatagan', FALSE, FALSE, FALSE, NULL, FALSE),

-- Family Dela Cruz
('Dela Cruz', 'Pedro', 'Gonzales', 'Jr.', 'Male', '1990-11-08', 'Calatagan', 33, 'Single', NULL, 0, 4, 'Luz Gonzales', 'Pedro Dela Cruz Sr.', 'Filipino', 'Iglesia ni Cristo', 'Fisherman', 'Elementary Graduate', '09182345678', 'Luz Dela Cruz', '09182345679', 'Dita', 'Barangay Balibago', 'Calatagan', FALSE, TRUE, FALSE, NULL, FALSE),

-- Family Flores  
('Flores', 'Miguel', 'Gutierrez', NULL, 'Male', '2000-02-18', 'Calatagan', 23, 'Single', NULL, 0, 5, 'Teresa Gutierrez', 'Ramon Gutierrez', 'Filipino', 'Roman Catholic', 'Student', 'College Level', '09215678901', 'Teresa Flores', '09215678902', 'Tulay na Bato', 'Barangay Balibago', 'Calatagan', FALSE, FALSE, FALSE, NULL, FALSE),

-- Family Fernandez
('Fernandez', 'Ricardo', 'Hernandez', NULL, 'Male', '1988-07-16', 'Tanauan', 35, 'Live-in', 'Angela Fernandez', 1, 1, 'Norma Hernandez', 'Victor Hernandez', 'Filipino', 'Roman Catholic', 'Mechanic', 'Vocational Graduate', '09260123456', 'Angela Fernandez', '09260123457', 'Dita', 'Barangay Balibago', 'Calatagan', TRUE, FALSE, FALSE, NULL, FALSE),
('Fernandez', 'Angela', 'Cruz', NULL, 'Female', '1991-05-20', 'Lipa', 32, 'Live-in', 'Ricardo Fernandez', 1, 2, 'Gloria Cruz', 'Rodolfo Cruz', 'Filipino', 'Roman Catholic', 'Beautician', 'Vocational Graduate', '09260123457', 'Ricardo Fernandez', '09260123456', 'Tulay na Bato', 'Barangay Balibago', 'Calatagan', TRUE, FALSE, FALSE, NULL, FALSE),

-- PWD
('Jimenez', 'Carlos', 'Reyes', NULL, 'Male', '1985-11-30', 'Calatagan', 38, 'Single', NULL, 0, 2, 'Corazon Reyes', 'Felipe Reyes', 'Filipino', 'Roman Catholic', 'Unemployed', 'High School Graduate', '09293456789', 'Corazon Jimenez', '09293456780', 'Dita', 'Barangay Balibago', 'Calatagan', TRUE, TRUE, FALSE, NULL, TRUE),

-- More Sitio 2 Families
('Martinez', 'Jose', 'Luna', NULL, 'Male', '1979-03-08', 'Manila', 44, 'Married', 'Elena Martinez', 4, 3, 'Rosa Luna', 'Domingo Luna', 'Filipino', 'Roman Catholic', 'Barangay Tanod', 'High School Graduate', '09391234567', 'Elena Martinez', '09391234568', 'Tulay na Bato', 'Barangay Balibago', 'Calatagan', TRUE, FALSE, FALSE, NULL, FALSE),
('Martinez', 'Elena', 'Soriano', NULL, 'Female', '1981-11-12', 'Batangas', 42, 'Married', 'Jose Martinez', 4, 2, 'Luisa Soriano', 'Mario Soriano', 'Filipino', 'Roman Catholic', 'Midwife', 'College Graduate', '09391234568', 'Jose Martinez', '09391234567', 'Dita', 'Barangay Balibago', 'Calatagan', TRUE, FALSE, FALSE, NULL, FALSE),
('Lim', 'David', 'Tan', NULL, 'Male', '1993-06-25', 'Manila', 30, 'Married', 'Joyce Lim', 2, 1, 'Susan Tan', 'Robert Tan', 'Filipino', 'Christian', 'Business Owner', 'College Graduate', '09402345678', 'Joyce Lim', '09402345679', 'Tulay na Bato', 'Barangay Balibago', 'Calatagan', TRUE, FALSE, FALSE, NULL, FALSE),
('Lim', 'Joyce', 'Go', NULL, 'Female', '1995-09-30', 'Lipa', 28, 'Married', 'David Lim', 2, 2, 'Betty Go', 'Henry Go', 'Filipino', 'Christian', 'Accountant', 'College Graduate', '09402345679', 'David Lim', '09402345678', 'Dita', 'Barangay Balibago', 'Calatagan', TRUE, FALSE, FALSE, NULL, FALSE),
('Diaz', 'Mario', 'Castro', NULL, 'Male', '1986-01-15', 'Tanauan', 37, 'Married', 'Sarah Diaz', 3, 2, 'Fe Castro', 'Luis Castro', 'Filipino', 'Roman Catholic', 'Electrician', 'Vocational Graduate', '09413456789', 'Sarah Diaz', '09413456780', 'Tulay na Bato', 'Barangay Balibago', 'Calatagan', TRUE, FALSE, FALSE, NULL, FALSE),
('Diaz', 'Sarah', 'Enriquez', NULL, 'Female', '1988-04-22', 'Batangas', 35, 'Married', 'Mario Diaz', 3, 1, 'Donna Enriquez', 'Frank Enriquez', 'Filipino', 'Roman Catholic', 'Nurse', 'College Graduate', '09413456780', 'Mario Diaz', '09413456789', 'Dita', 'Barangay Balibago', 'Calatagan', TRUE, FALSE, FALSE, NULL, FALSE),
('Gutierrez', 'Antonio', 'Morales', NULL, 'Male', '1974-08-10', 'Manila', 49, 'Married', 'Nenita Gutierrez', 3, 4, 'Paz Morales', 'Andres Morales', 'Filipino', 'Roman Catholic', 'Plumber', 'Elementary Graduate', '09424567890', 'Nenita Gutierrez', '09424567891', 'Tulay na Bato', 'Barangay Balibago', 'Calatagan', TRUE, TRUE, FALSE, NULL, FALSE),
('Gutierrez', 'Nenita', 'Ramos', NULL, 'Female', '1976-12-18', 'Lipa', 47, 'Married', 'Antonio Gutierrez', 3, 3, 'Delia Ramos', 'Oscar Ramos', 'Filipino', 'Roman Catholic', 'Housewife', 'High School Graduate', '09424567891', 'Antonio Gutierrez', '09424567890', 'Dita', 'Barangay Balibago', 'Calatagan', TRUE, TRUE, FALSE, NULL, FALSE),
('Perez', 'Ronaldo', 'Villa', NULL, 'Male', '1997-02-05', 'Calatagan', 26, 'Single', NULL, 0, 3, 'Nora Villa', 'Rene Villa', 'Filipino', 'Seventh-day Adventist', 'Call Center Agent', 'College Graduate', '09435678901', 'Nora Perez', '09435678902', 'Tulay na Bato', 'Barangay Balibago', 'Calatagan', TRUE, FALSE, FALSE, NULL, FALSE),
('Salazar', 'Marissa', 'Abad', NULL, 'Female', '1984-07-28', 'Batangas', 39, 'Widowed', NULL, 2, 2, 'Cora Abad', 'Bert Abad', 'Filipino', 'Roman Catholic', 'Market Vendor', 'Elementary Graduate', '09446789012', 'Cora Salazar', '09446789013', 'Dita', 'Barangay Balibago', 'Calatagan', TRUE, TRUE, TRUE, 'SP-2019-203', TRUE),
('Valdez', 'Arnold', 'Cruz', NULL, 'Male', '1989-10-12', 'Taal', 34, 'Divorced', NULL, 1, 1, 'Betty Cruz', 'Allan Cruz', 'Filipino', 'Born Again', 'Welder', 'Vocational Graduate', '09457890123', 'Betty Valdez', '09457890124', 'Tulay na Bato', 'Barangay Balibago', 'Calatagan', TRUE, FALSE, FALSE, NULL, FALSE),
('Ocampo', 'Jasmine', 'Fernandez', NULL, 'Female', '2001-03-18', 'Lipa', 22, 'Single', NULL, 0, 2, 'Amy Fernandez', 'Jun Fernandez', 'Filipino', 'Roman Catholic', 'Sales Clerk', 'Senior High Graduate', '09468901234', 'Amy Ocampo', '09468901235', 'Dita', 'Barangay Balibago', 'Calatagan', TRUE, FALSE, FALSE, NULL, FALSE),
('Torres', 'Gary', 'Manuel', NULL, 'Male', '1982-11-20', 'Manila', 41, 'Married', 'Susan Torres', 2, 2, 'Nena Manuel', 'Gil Manuel', 'Filipino', 'Iglesia ni Cristo', 'Security Guard', 'High School Graduate', '09479012345', 'Susan Torres', '09479012346', 'Tulay na Bato', 'Barangay Balibago', 'Calatagan', TRUE, FALSE, FALSE, NULL, FALSE),
('Torres', 'Susan', 'Pablo', NULL, 'Female', '1985-05-15', 'Batangas', 38, 'Married', 'Gary Torres', 2, 3, 'Letty Pablo', 'Boy Pablo', 'Filipino', 'Iglesia ni Cristo', 'Factory Worker', 'High School Graduate', '09479012346', 'Gary Torres', '09479012345', 'Dita', 'Barangay Balibago', 'Calatagan', TRUE, FALSE, FALSE, NULL, FALSE),

-- KAWAYANAN, KUDRADO RESIDENTS (25 people)
-- Family Villanueva
('Villanueva', 'Eduardo', 'Santiago', NULL, 'Male', '1975-10-05', 'Manila', 48, 'Married', 'Rosalie Villanueva', 4, 2, 'Linda Santiago', 'Eduardo Santiago Sr.', 'Filipino', 'Roman Catholic', 'Barangay Tanod', 'College Graduate', '09237890123', 'Rosalie Villanueva', '09237890124', 'Kawayanan', 'Barangay Balibago', 'Calatagan', TRUE, FALSE, FALSE, NULL, FALSE),
('Villanueva', 'Rosalie', 'Dizon', NULL, 'Female', '1977-12-28', 'Batangas', 46, 'Married', 'Eduardo Villanueva', 4, 3, 'Cecilia Dizon', 'Romeo Dizon', 'Filipino', 'Roman Catholic', 'Dressmaker', 'Vocational Graduate', '09237890124', 'Eduardo Villanueva', '09237890123', 'Kudrado', 'Barangay Balibago', 'Calatagan', TRUE, FALSE, FALSE, NULL, FALSE),
('Villanueva', 'Ed Jr.', 'Dizon', NULL, 'Male', '2000-06-15', 'Calatagan', 23, 'Single', NULL, 0, 3, 'Rosalie Villanueva', 'Eduardo Villanueva', 'Filipino', 'Roman Catholic', 'Driver', 'High School Graduate', '09237890123', 'Rosalie Villanueva', '09237890124', 'Kawayanan', 'Barangay Balibago', 'Calatagan', TRUE, FALSE, FALSE, NULL, FALSE),

-- Family Morales
('Morales', 'Josephine', 'Rivera', NULL, 'Female', '1998-04-27', 'Batangas City', 25, 'Single', NULL, 0, 4, 'Gloria Rivera', 'Antonio Rivera', 'Filipino', 'Seventh-day Adventist', 'Call Center Agent', 'College Graduate', '09248901234', 'Gloria Morales', '09248901235', 'Kudrado', 'Barangay Balibago', 'Calatagan', TRUE, FALSE, FALSE, NULL, FALSE),

-- Senior Citizens
('Domingo', 'Alfredo', 'Cruz', NULL, 'Male', '1955-03-22', 'Manila', 68, 'Married', 'Erlinda Domingo', 7, 6, 'Carmen Cruz', 'Alfonso Cruz', 'Filipino', 'Roman Catholic', 'Retired Seaman', 'High School Graduate', '09282345678', 'Erlinda Domingo', '09282345679', 'Kawayanan', 'Barangay Balibago', 'Calatagan', TRUE, FALSE, FALSE, NULL, FALSE),
('Domingo', 'Erlinda', 'Santos', NULL, 'Female', '1957-08-10', 'Lipa', 66, 'Married', 'Alfredo Domingo', 7, 4, 'Josefa Santos', 'Miguel Santos', 'Filipino', 'Roman Catholic', 'Retired', 'Elementary Graduate', '09282345679', 'Alfredo Domingo', '09282345678', 'Kudrado', 'Barangay Balibago', 'Calatagan', TRUE, FALSE, FALSE, NULL, FALSE),
('Rodriguez', 'Francisco', 'Gomez', NULL, 'Male', '1952-11-05', 'Manila', 71, 'Widowed', NULL, 5, 5, 'Esperanza Gomez', 'Pablo Gomez', 'Filipino', 'Roman Catholic', 'Retired Fisherman', 'Elementary Graduate', '09480123456', 'Ed Villanueva', '09237890123', 'Kawayanan', 'Barangay Balibago', 'Calatagan', TRUE, TRUE, FALSE, NULL, FALSE),

-- More Sitio 3 Families
('Pascual', 'Vicente', 'Hernandez', NULL, 'Male', '1987-02-14', 'Batangas', 36, 'Married', 'Diana Pascual', 3, 2, 'Aida Hernandez', 'Virgilio Hernandez', 'Filipino', 'Roman Catholic', 'Farmer', 'Elementary Graduate', '09491234567', 'Diana Pascual', '09491234568', 'Kudrado', 'Barangay Balibago', 'Calatagan', TRUE, TRUE, FALSE, NULL, TRUE),
('Pascual', 'Diana', 'Estrada', NULL, 'Female', '1989-07-20', 'Lipa', 34, 'Married', 'Vicente Pascual', 3, 1, 'Emily Estrada', 'Willie Estrada', 'Filipino', 'Roman Catholic', 'Housewife', 'High School Graduate', '09491234568', 'Vicente Pascual', '09491234567', 'Kawayanan', 'Barangay Balibago', 'Calatagan', TRUE, TRUE, FALSE, NULL, TRUE),
('Santos', 'Roberto', 'Aquino', NULL, 'Male', '1983-09-25', 'Taal', 40, 'Married', 'Marites Santos', 2, 3, 'Pilar Aquino', 'Ernesto Aquino', 'Filipino', 'Born Again', 'Electrician', 'Vocational Graduate', '09502345678', 'Marites Santos', '09502345679', 'Kudrado', 'Barangay Balibago', 'Calatagan', TRUE, FALSE, FALSE, NULL, FALSE),
('Santos', 'Marites', 'Padilla', NULL, 'Female', '1985-12-08', 'Calatagan', 38, 'Married', 'Roberto Santos', 2, 2, 'Edna Padilla', 'Cesar Padilla', 'Filipino', 'Born Again', 'Online Seller', 'College Level', '09502345679', 'Roberto Santos', '09502345678', 'Kawayanan', 'Barangay Balibago', 'Calatagan', TRUE, FALSE, FALSE, NULL, FALSE),
('Mercado', 'Nelson', 'Villanueva', NULL, 'Male', '1991-01-12', 'Manila', 32, 'Single', NULL, 0, 2, 'Myrna Villanueva', 'Nestor Villanueva', 'Filipino', 'Christian', 'IT Support', 'College Graduate', '09513456789', 'Myrna Mercado', '09513456780', 'Kudrado', 'Barangay Balibago', 'Calatagan', TRUE, FALSE, FALSE, NULL, FALSE),
('Reyes', 'Maricel', 'Gonzales', NULL, 'Female', '1994-05-18', 'Lipa', 29, 'Live-in', 'Kevin Reyes', 1, 1, 'Nelia Gonzales', 'Roland Gonzales', 'Filipino', 'Roman Catholic', 'Cashier', 'High School Graduate', '09524567890', 'Kevin Reyes', '09524567891', 'Kawayanan', 'Barangay Balibago', 'Calatagan', TRUE, TRUE, FALSE, NULL, TRUE),
('Reyes', 'Kevin', 'Mercado', NULL, 'Male', '1993-08-30', 'Batangas', 30, 'Live-in', 'Maricel Reyes', 1, 2, 'Tess Mercado', 'Randy Mercado', 'Filipino', 'Roman Catholic', 'Welder', 'Vocational Graduate', '09524567891', 'Maricel Reyes', '09524567890', 'Kudrado', 'Barangay Balibago', 'Calatagan', TRUE, TRUE, FALSE, NULL, TRUE),
('Gomez', 'Clarissa', 'Ramos', NULL, 'Female', '1986-03-05', 'Tanauan', 37, 'Separated', NULL, 2, 3, 'Cynthia Ramos', 'Rudy Ramos', 'Filipino', 'Roman Catholic', 'Laundrywoman', 'High School Graduate', '09535678901', 'Cynthia Gomez', '09535678902', 'Kawayanan', 'Barangay Balibago', 'Calatagan', TRUE, TRUE, TRUE, 'SP-2018-156', TRUE),
('Cruz', 'Jerome', 'Castro', NULL, 'Male', '1999-11-22', 'Calatagan', 24, 'Single', NULL, 0, 1, 'Gemma Castro', 'Joel Castro', 'Filipino', 'Iglesia ni Cristo', 'Motorcycle Mechanic', 'Vocational Graduate', '09546789012', 'Gemma Cruz', '09546789013', 'Kudrado', 'Barangay Balibago', 'Calatagan', TRUE, FALSE, FALSE, NULL, FALSE),
('Hernandez', 'Jennifer', 'Torres', NULL, 'Female', '2002-06-10', 'Lipa', 21, 'Single', NULL, 0, 2, 'Loida Torres', 'Jimmy Torres', 'Filipino', 'Roman Catholic', 'Waitress', 'Senior High Graduate', '09557890123', 'Loida Hernandez', '09557890124', 'Kawayanan', 'Barangay Balibago', 'Calatagan', FALSE, FALSE, FALSE, NULL, FALSE),
('Alvarez', 'Patrick', 'Diaz', NULL, 'Male', '1981-04-16', 'Manila', 42, 'Divorced', NULL, 1, 1, 'Vicky Diaz', 'Pete Diaz', 'Filipino', 'Roman Catholic', 'Painter', 'Elementary Graduate', '09568901234', 'Vicky Alvarez', '09568901235', 'Kudrado', 'Barangay Balibago', 'Calatagan', TRUE, TRUE, FALSE, NULL, FALSE),
('Castro', 'Carmela', 'Velasco', NULL, 'Female', '1990-09-12', 'Batangas', 33, 'Married', 'Luis Castro', 1, 2, 'Lorna Velasco', 'Ernie Velasco', 'Filipino', 'Roman Catholic', 'Receptionist', 'College Level', '09579012345', 'Luis Castro', '09579012346', 'Kawayanan', 'Barangay Balibago', 'Calatagan', TRUE, FALSE, FALSE, NULL, FALSE),
('Castro', 'Luis', 'Flores', NULL, 'Male', '1988-12-01', 'Lipa', 35, 'Married', 'Carmela Castro', 1, 3, 'Dina Flores', 'Larry Flores', 'Filipino', 'Roman Catholic', 'Pool Maintenance', 'Vocational Graduate', '09579012346', 'Carmela Castro', '09579012345', 'Kudrado', 'Barangay Balibago', 'Calatagan', TRUE, FALSE, FALSE, NULL, FALSE),
('Mendoza', 'Ryan', 'Gutierrez', NULL, 'Male', '1996-07-08', 'Taal', 27, 'Single', NULL, 0, 4, 'Marilyn Gutierrez', 'Rico Gutierrez', 'Filipino', 'Born Again', 'Warehouse Staff', 'High School Graduate', '09580123456', 'Marilyn Mendoza', '09580123457', 'Kawayanan', 'Barangay Balibago', 'Calatagan', TRUE, FALSE, FALSE, NULL, FALSE);

-- Display summary
SELECT COUNT(*) as 'Total Residents Added' FROM residents;

SELECT 
    'Gender Distribution' as 'Category',
    gender as 'Value',
    COUNT(*) as 'Count'
FROM residents
GROUP BY gender

UNION ALL

SELECT 
    'Civil Status' as 'Category',
    civil_status as 'Value',
    COUNT(*) as 'Count'
FROM residents
GROUP BY civil_status

UNION ALL

SELECT 
    'Sitio Distribution' as 'Category',
    sitio as 'Value',
    COUNT(*) as 'Count'
FROM residents
GROUP BY sitio

UNION ALL

SELECT 
    'Voter Status' as 'Category',
    CASE WHEN registered_voter = 1 THEN 'Registered' ELSE 'Not Registered' END as 'Value',
    COUNT(*) as 'Count'
FROM residents
GROUP BY registered_voter

UNION ALL

SELECT 
    '4Ps Members' as 'Category',
    CASE WHEN fourps_member = 1 THEN 'Yes' ELSE 'No' END as 'Value',
    COUNT(*) as 'Count'
FROM residents
GROUP BY fourps_member

ORDER BY Category, Value;
