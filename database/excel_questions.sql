USE smartcareer;

INSERT INTO questions
(subject, question_text, option_a, option_b, option_c, option_d, correct_option, explanation, difficulty)
VALUES
-- Easy (10)
('Excel','What is the file extension of an Excel workbook?','.txt','.xls or .xlsx','.csv','.doc','B','Excel files use .xls or .xlsx.','Easy'),
('Excel','Which symbol is used to start a formula in Excel?','=','+','-','@','A','All formulas begin with = sign.','Easy'),
('Excel','Shortcut to save a file in Excel?','Ctrl+S','Ctrl+Shift+S','Alt+S','Ctrl+Alt+S','A','Ctrl+S saves current workbook.','Easy'),
('Excel','SUM function does what?','Counts','Adds values','Subtracts','Averages','B','SUM adds all numeric values.','Easy'),
('Excel','Which function finds average?','COUNT','SUM','AVERAGE','MAX','C','AVERAGE calculates mean.','Easy'),
('Excel','Which key moves to next cell right?','Tab','Enter','Shift','Ctrl','A','Tab moves to right cell.','Easy'),
('Excel','Which chart shows data in columns?','Pie','Column','Line','Scatter','B','Column chart shows vertical bars.','Easy'),
('Excel','What does COUNT function do?','Adds numbers','Counts numeric cells','Counts all cells','None','B','COUNT counts numeric values only.','Easy'),
('Excel','Which function returns largest value?','MAX','MIN','LARGE','TOP','A','MAX gives highest value.','Easy'),
('Excel','Which feature copies format quickly?','AutoFill','Format Painter','Copy','Filter','B','Format Painter copies formatting.','Easy'),

-- Medium (12)
('Excel','Absolute cell reference example?','A1','$A$1','A$1','$A1','B','Both column and row fixed.','Medium'),
('Excel','VLOOKUP stands for?','Vertical Lookup','Value Lookup','Variable Lookup','Vector Lookup','A','VLOOKUP searches vertically.','Medium'),
('Excel','Which function counts non-empty cells?','COUNT','COUNTA','COUNTIF','SUM','B','COUNTA counts all non-empty.','Medium'),
('Excel','Conditional formatting used for?','Filter data','Highlight based on rules','Copy formulas','Sort data','B','Visually highlights rules.','Medium'),
('Excel','Pivot Table used for?','Charts','Summarizing data','Formatting','Graphs','B','Summarizes large data quickly.','Medium'),
('Excel','IF function syntax?','IF(test, true, false)','IF(value)','IF(true, false)','IF(condition)','A','Basic conditional function.','Medium'),
('Excel','Which shortcut inserts new row?','Ctrl+R','Ctrl+Shift++','Alt+N','Ctrl+Enter','B','Ctrl+Shift++ adds row.','Medium'),
('Excel','Freeze Panes used for?','Lock rows/columns','Sort data','Hide data','Copy data','A','Locks rows/columns visible.','Medium'),
('Excel','Data validation prevents?','Empty cells','Wrong data entry','Formatting','Formulas','B','Restricts input type.','Medium'),
('Excel','Which function returns current date?','NOW()','DATE()','TODAY()','TIME()','C','TODAY() gives current date.','Medium'),
('Excel','Filter vs Sort difference?','Sort hides data','Filter hides, Sort rearranges','Both same','None','B','Filter hides rows temporarily.','Medium'),
('Excel','Concatenate joins?','Text strings','Numbers','Dates','Sheets','A','Joins multiple text cells.','Medium'),

-- Hard (8)
('Excel','What does INDEX-MATCH replace?','SUM','VLOOKUP','COUNT','AVERAGE','B','Combination used instead of VLOOKUP.','Hard'),
('Excel','Dynamic named ranges created using?','OFFSET','SUM','AVERAGE','FILTER','A','OFFSET defines range dynamically.','Hard'),
('Excel','Array formula executes?','Multiple values','Single value','One cell only','None','A','Performs multiple calc at once.','Hard'),
('Excel','Power Query used for?','Formatting','Data transformation','Pivot table','Charts','B','Transforms and cleans data.','Hard'),
('Excel','Goal Seek used to?','Forecast data','Find input for desired output','Format cells','Filter data','B','Finds required input value.','Hard'),
('Excel','What does INDIRECT do?','Returns cell reference from text','Returns text','Counts range','Finds data','A','Converts text to reference.','Hard'),
('Excel','Dynamic dashboards use?','Charts only','Pivot tables, slicers, formulas','Macros only','Manual input','B','Uses slicers & pivots.','Hard'),
('Excel','Power Pivot is used for?','Macros','Large data modeling','Charts','Conditional formatting','B','For large data analysis.','Hard');
