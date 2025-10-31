USE smartcareer;

INSERT INTO questions
(subject, question_text, option_a, option_b, option_c, option_d, correct_option, explanation, difficulty)
VALUES
-- Easy SQL (15)
('SQL', 'Which command is used to retrieve data from a database?', 'GET', 'SELECT', 'RETRIEVE', 'FETCH', 'B', 'SELECT statement retrieves data from one or more tables.', 'Easy'),
('SQL', 'What does the WHERE clause do?', 'Sorts data', 'Filters rows', 'Groups data', 'Joins tables', 'B', 'WHERE clause filters rows based on specified conditions.', 'Easy'),
('SQL', 'Which keyword removes duplicate rows?', 'UNIQUE', 'DISTINCT', 'REMOVE', 'DELETE', 'B', 'DISTINCT eliminates duplicate rows from result set.', 'Easy'),
('SQL', 'What does ORDER BY do?', 'Creates order', 'Sorts results', 'Filters data', 'Groups data', 'B', 'ORDER BY sorts query results by specified columns.', 'Easy'),
('SQL', 'Which clause groups rows?', 'GROUP BY', 'GATHER', 'COLLECT', 'BUNCH', 'A', 'GROUP BY groups rows with same values into summary rows.', 'Easy'),
('SQL', 'What does INSERT INTO do?', 'Updates data', 'Adds new rows', 'Deletes rows', 'Modifies table', 'B', 'INSERT INTO adds new rows to a table.', 'Easy'),
('SQL', 'Which command deletes rows?', 'REMOVE', 'DELETE', 'DROP', 'CLEAR', 'B', 'DELETE removes rows from a table based on condition.', 'Easy'),
('SQL', 'What does UPDATE do?', 'Adds rows', 'Modifies existing rows', 'Deletes rows', 'Creates table', 'B', 'UPDATE modifies existing data in a table.', 'Easy'),
('SQL', 'Which constraint ensures unique values?', 'PRIMARY KEY', 'FOREIGN KEY', 'UNIQUE', 'CHECK', 'C', 'UNIQUE constraint ensures all values in column are different.', 'Easy'),
('SQL', 'What does CREATE TABLE do?', 'Adds data', 'Creates new table', 'Modifies table', 'Deletes table', 'B', 'CREATE TABLE creates a new table structure.', 'Easy'),
('SQL', 'Which function returns row count?', 'SUM()', 'COUNT()', 'TOTAL()', 'NUMBER()', 'B', 'COUNT() returns number of rows matching query criteria.', 'Easy'),
('SQL', 'What does DROP TABLE do?', 'Empties table', 'Deletes table structure', 'Modifies table', 'Creates backup', 'B', 'DROP TABLE permanently deletes table and its data.', 'Easy'),
('SQL', 'Which operator matches patterns?', 'MATCH', 'LIKE', 'SIMILAR', 'PATTERN', 'B', 'LIKE operator matches string patterns using wildcards.', 'Easy'),
('SQL', 'What does ALTER TABLE do?', 'Creates table', 'Modifies table structure', 'Deletes table', 'Views table', 'B', 'ALTER TABLE modifies existing table structure.', 'Easy'),
('SQL', 'Which clause filters groups?', 'WHERE', 'HAVING', 'FILTER', 'SELECT', 'B', 'HAVING filters groups after GROUP BY, WHERE filters rows before.', 'Easy'),

-- Medium SQL (15)
('SQL', 'What is the difference between DELETE and TRUNCATE?', 'No difference', 'DELETE can be rolled back, TRUNCATE cannot', 'TRUNCATE is slower', 'DELETE removes table', 'B', 'DELETE can be rolled back and triggers fire, TRUNCATE is faster but permanent.', 'Medium'),
('SQL', 'What is a foreign key?', 'Primary identifier', 'References primary key in another table', 'Unique constraint', 'Index type', 'B', 'Foreign key creates relationship by referencing primary key in another table.', 'Medium'),
('SQL', 'What does INNER JOIN return?', 'All rows', 'Only matching rows from both tables', 'Left table rows', 'Right table rows', 'B', 'INNER JOIN returns only rows with matching values in both tables.', 'Medium'),
('SQL', 'What is a subquery?', 'A function', 'Query inside another query', 'A view', 'A stored procedure', 'B', 'Subquery is query nested inside another query.', 'Medium'),
('SQL', 'What does the IN operator do?', 'Checks range', 'Checks if value in list', 'Joins tables', 'Sorts data', 'B', 'IN operator checks if value matches any value in a list.', 'Medium'),
('SQL', 'What is normalization?', 'Data encryption', 'Organizing data to reduce redundancy', 'Data sorting', 'Data backup', 'B', 'Normalization organizes data to minimize redundancy and dependency.', 'Medium'),
('SQL', 'What does UNION do?', 'Joins tables horizontally', 'Combines results of two queries', 'Filters data', 'Groups data', 'B', 'UNION combines result sets of two or more SELECT statements.', 'Medium'),
('SQL', 'What is an index?', 'A constraint', 'Data structure for fast retrieval', 'A primary key', 'A foreign key', 'B', 'Index improves query performance by providing fast data access.', 'Medium'),
('SQL', 'What does the COALESCE function do?', 'Counts nulls', 'Returns first non-null value', 'Removes nulls', 'Creates nulls', 'B', 'COALESCE returns first non-null value from argument list.', 'Medium'),
('SQL', 'What is a view?', 'A table', 'Virtual table based on query', 'An index', 'A constraint', 'B', 'View is virtual table representing result of stored query.', 'Medium'),
('SQL', 'What does CROSS JOIN do?', 'Matches rows', 'Returns cartesian product', 'Filters rows', 'Groups rows', 'B', 'CROSS JOIN returns cartesian product of two tables.', 'Medium'),
('SQL', 'What is a stored procedure?', 'A function', 'Precompiled SQL code', 'A table', 'A view', 'B', 'Stored procedure is precompiled SQL code stored in database.', 'Medium'),
('SQL', 'What does the CASE statement do?', 'Creates cases', 'Provides conditional logic', 'Filters data', 'Groups data', 'B', 'CASE provides if-then-else logic in SQL queries.', 'Medium'),
('SQL', 'What is a trigger?', 'A constraint', 'Automatically executed code on events', 'A function', 'An index', 'B', 'Trigger is code automatically executed in response to events.', 'Medium'),
('SQL', 'What does GROUP_CONCAT do?', 'Groups strings', 'Concatenates values from group', 'Joins tables', 'Counts groups', 'B', 'GROUP_CONCAT concatenates values from multiple rows into single string.', 'Medium'),

-- Hard SQL (10)
('SQL', 'What is a window function?', 'A view', 'Function that operates on set of rows', 'A join type', 'A constraint', 'B', 'Window functions perform calculations across set of rows related to current row.', 'Hard'),
('SQL', 'What does the PARTITION BY clause do?', 'Divides table', 'Divides result set into partitions', 'Creates partitions', 'Filters partitions', 'B', 'PARTITION BY divides result set for window function calculation.', 'Hard'),
('SQL', 'What is a CTE (Common Table Expression)?', 'A table', 'Temporary result set', 'A view', 'A stored procedure', 'B', 'CTE is temporary named result set that exists within scope of single statement.', 'Hard'),
('SQL', 'What does the EXPLAIN command do?', 'Adds comments', 'Shows query execution plan', 'Validates syntax', 'Creates documentation', 'B', 'EXPLAIN shows how database will execute query.', 'Hard'),
('SQL', 'What is database sharding?', 'Data backup', 'Horizontal partitioning across databases', 'Data encryption', 'Data compression', 'B', 'Sharding splits data across multiple databases to improve scalability.', 'Hard'),
('SQL', 'What is the N+1 query problem?', 'Syntax error', 'Executing N queries after initial query', 'Index problem', 'Connection issue', 'B', 'N+1 problem occurs when application makes N additional queries for each row.', 'Hard'),
('SQL', 'What does the OVER clause do?', 'Overrides data', 'Defines window for window functions', 'Creates view', 'Joins tables', 'B', 'OVER defines window specification for window functions.', 'Hard'),
('SQL', 'What is ACID in databases?', 'Query language', 'Transaction properties (Atomicity, Consistency, Isolation, Durability)', 'Index type', 'Backup method', 'B', 'ACID defines properties ensuring reliable database transactions.', 'Hard'),
('SQL', 'What is a materialized view?', 'Normal view', 'Physically stored query result', 'Temporary view', 'Virtual view', 'B', 'Materialized view stores query results physically for faster access.', 'Hard'),
('SQL', 'What does the UPSERT operation do?', 'Updates only', 'Updates if exists, inserts if not', 'Inserts only', 'Deletes and inserts', 'B', 'UPSERT updates existing row or inserts new one if not exists.', 'Hard');