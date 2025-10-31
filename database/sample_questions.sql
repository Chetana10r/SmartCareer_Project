-- Python Questions
INSERT INTO questions (subject, question_text, option_a, option_b, option_c, option_d, correct_option, explanation, difficulty) VALUES
('Python', 'What is the output of: print(type([]) is list)?', 'True', 'False', 'None', 'Error', 'A', 'The is operator checks for identity. Since [] creates a list, type([]) is list returns True.', 'Easy'),
('Python', 'Which method is used to remove whitespace from both ends of a string?', 'trim()', 'strip()', 'remove()', 'cut()', 'B', 'strip() removes whitespace from both ends. lstrip() removes from left, rstrip() from right.', 'Easy'),
('Python', 'What is the time complexity of accessing an element in a Python list by index?', 'O(1)', 'O(n)', 'O(log n)', 'O(n²)', 'A', 'List indexing in Python is O(1) because lists are implemented as dynamic arrays.', 'Medium'),
('Python', 'Which keyword is used to define a function that returns a generator?', 'return', 'yield', 'generate', 'async', 'B', 'yield is used in generator functions to produce values one at a time without storing the entire sequence in memory.', 'Medium'),
('Python', 'What does the __init__ method do in a Python class?', 'Creates a new class', 'Initializes object attributes', 'Deletes an object', 'Imports modules', 'B', '__init__ is the constructor method that initializes object attributes when an instance is created.', 'Easy');

-- SQL Questions
INSERT INTO questions (subject, question_text, option_a, option_b, option_c, option_d, correct_option, explanation, difficulty) VALUES
('SQL', 'Which SQL clause is used to filter records?', 'FILTER', 'WHERE', 'HAVING', 'SELECT', 'B', 'WHERE clause filters rows before grouping. HAVING filters after GROUP BY.', 'Easy'),
('SQL', 'What is the difference between INNER JOIN and LEFT JOIN?', 'No difference', 'LEFT JOIN includes unmatched left table rows', 'INNER JOIN is faster', 'LEFT JOIN requires indexes', 'B', 'LEFT JOIN returns all rows from left table plus matched rows from right. INNER JOIN only returns matching rows.', 'Medium'),
('SQL', 'Which aggregate function returns the number of rows?', 'SUM()', 'COUNT()', 'NUMBER()', 'TOTAL()', 'B', 'COUNT() returns the number of rows that match the query criteria.', 'Easy'),
('SQL', 'What does DISTINCT keyword do in SQL?', 'Sorts results', 'Removes duplicates', 'Counts rows', 'Joins tables', 'B', 'DISTINCT eliminates duplicate rows from the result set.', 'Easy'),
('SQL', 'Which constraint ensures all values in a column are unique?', 'PRIMARY KEY', 'UNIQUE', 'CHECK', 'NOT NULL', 'B', 'UNIQUE constraint ensures all values are different. PRIMARY KEY combines UNIQUE and NOT NULL.', 'Easy');

-- Machine Learning Questions
INSERT INTO questions (subject, question_text, option_a, option_b, option_c, option_d, correct_option, explanation, difficulty) VALUES
('Machine Learning', 'What is overfitting in machine learning?', 'Model performs well on training data but poorly on test data', 'Model performs poorly on all data', 'Model is too simple', 'Model trains too fast', 'A', 'Overfitting occurs when model learns training data too well, including noise, leading to poor generalization.', 'Medium'),
('Machine Learning', 'Which algorithm is best for binary classification?', 'K-Means', 'Logistic Regression', 'PCA', 'DBSCAN', 'B', 'Logistic Regression is specifically designed for binary classification problems.', 'Easy'),
('Machine Learning', 'What does cross-validation help prevent?', 'Underfitting', 'Overfitting', 'Data leakage', 'Feature scaling', 'B', 'Cross-validation helps assess model generalization and prevents overfitting by testing on multiple data splits.', 'Medium'),
('Machine Learning', 'Which metric is best for imbalanced datasets?', 'Accuracy', 'F1-Score', 'MSE', 'R²', 'B', 'F1-Score balances precision and recall, making it better for imbalanced datasets than accuracy.', 'Medium'),
('Machine Learning', 'What is the purpose of feature scaling?', 'Reduce overfitting', 'Normalize feature ranges', 'Increase accuracy', 'Remove outliers', 'B', 'Feature scaling normalizes ranges so features contribute equally to distance-based algorithms.', 'Easy');

-- Deep Learning Questions
INSERT INTO questions (subject, question_text, option_a, option_b, option_c, option_d, correct_option, explanation, difficulty) VALUES
('Deep Learning', 'What is the vanishing gradient problem?', 'Gradients become too large', 'Gradients become very small', 'No gradients calculated', 'Gradients are constant', 'B', 'In deep networks, gradients can become extremely small during backpropagation, making learning very slow.', 'Medium'),
('Deep Learning', 'Which activation function helps solve vanishing gradient?', 'Sigmoid', 'Tanh', 'ReLU', 'Linear', 'C', 'ReLU (Rectified Linear Unit) helps mitigate vanishing gradient as its gradient is 1 for positive values.', 'Medium'),
('Deep Learning', 'What is dropout in neural networks?', 'Removing features', 'Randomly disabling neurons during training', 'Stopping training early', 'Reducing layers', 'B', 'Dropout randomly deactivates neurons during training to prevent overfitting and improve generalization.', 'Medium'),
('Deep Learning', 'Which layer is used for image classification CNNs?', 'LSTM', 'Dense', 'Convolutional', 'Embedding', 'C', 'Convolutional layers extract spatial features from images using learnable filters.', 'Easy'),
('Deep Learning', 'What is batch normalization used for?', 'Increase batch size', 'Normalize layer inputs', 'Reduce training time', 'Add regularization', 'B', 'Batch normalization normalizes inputs to each layer, stabilizing and accelerating training.', 'Medium');

-- Aptitude Questions
INSERT INTO questions (subject, question_text, option_a, option_b, option_c, option_d, correct_option, explanation, difficulty) VALUES
('Aptitude', 'If a train travels 60 km in 45 minutes, what is its speed in km/h?', '60', '75', '80', '90', 'C', 'Speed = Distance/Time. 60km / (45/60)hours = 60 × (60/45) = 80 km/h', 'Easy'),
('Aptitude', 'What is 15% of 200?', '25', '30', '35', '40', 'B', '15% of 200 = (15/100) × 200 = 30', 'Easy'),
('Aptitude', 'A series: 2, 6, 12, 20, 30, ?. What comes next?', '38', '40', '42', '44', 'C', 'Differences: 4,6,8,10... Next difference is 12, so 30+12=42', 'Medium'),
('Aptitude', 'If 5 workers complete a task in 12 days, how many days for 10 workers?', '6', '8', '10', '24', 'A', 'Inverse proportion: 5×12 = 10×x, so x = 60/10 = 6 days', 'Easy'),
('Aptitude', 'In a class of 50 students, 30 play cricket and 25 play football. 10 play both. How many play neither?', '5', '10', '15', '20', 'A', 'Only cricket: 20, Only football: 15, Both: 10. Total = 45. Neither = 50-45 = 5', 'Medium');

-- Excel Questions
INSERT INTO questions (subject, question_text, option_a, option_b, option_c, option_d, correct_option, explanation, difficulty) VALUES
('Excel', 'Which function calculates the average of a range?', 'SUM()', 'AVERAGE()', 'MEAN()', 'AVG()', 'B', 'AVERAGE() function calculates arithmetic mean of selected cells.', 'Easy'),
('Excel', 'What does VLOOKUP do?', 'Validates data', 'Searches vertically in first column', 'Locks cells', 'Validates formulas', 'B', 'VLOOKUP searches for a value in the first column and returns value from another column in same row.', 'Easy'),
('Excel', 'Which formula concatenates text in cells A1 and B1?', 'JOIN(A1,B1)', 'CONCAT(A1,B1)', 'A1&B1', 'Both B and C', 'D', 'Both CONCAT() function and & operator can concatenate text in Excel.', 'Easy'),
('Excel', 'What does $ symbol do in cell references?', 'Formats as currency', 'Makes reference absolute', 'Adds formula', 'Creates pivot table', 'B', '$ makes cell reference absolute, preventing it from changing when formula is copied.', 'Easy'),
('Excel', 'Which function counts cells with numbers only?', 'COUNT()', 'COUNTA()', 'COUNTIF()', 'COUNTNUMS()', 'A', 'COUNT() counts only cells containing numbers. COUNTA() counts non-empty cells.', 'Easy');