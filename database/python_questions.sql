USE smartcareer;

INSERT INTO questions
(subject, question_text, option_a, option_b, option_c, option_d, correct_option, explanation, difficulty)
VALUES
-- Easy (15)
('Python','Which keyword is used to define a function in Python?','function','def','func','define','B','def keyword defines a function.','Easy'),
('Python','What is the output of print(3**2)?','5','6','9','8','C','** is exponentiation operator.','Easy'),
('Python','Which data type is mutable in Python?','tuple','string','list','int','C','Lists are mutable.','Easy'),
('Python','What does len() return?','Length','Type','Value','Index','A','len() gives number of items.','Easy'),
('Python','Which operator is for floor division?','/','//','%','**','B','// gives floor division.','Easy'),
('Python','Which is correct way to create a dictionary?','[]','()','{}','<>','C','{} creates dict.','Easy'),
('Python','Which method adds an element to list end?','add()','append()','insert()','push()','B','append() adds to end.','Easy'),
('Python','Output of print(bool(0))?','True','False','0','None','B','0 is False.','Easy'),
('Python','Keyword for exception handling?','try','catch','handle','except','A','try...except used.','Easy'),
('Python','range(5) returns?','1-5','0-4','0-5','1-4','B','0-4 excluding 5.','Easy'),
('Python','Method to remove and return last element?','remove()','pop()','delete()','clear()','B','pop() removes and returns.','Easy'),
('Python','type("Hello") returns?','int','str','string','text','B','Strings are of type str.','Easy'),
('Python','Keyword to create class?','class','Class','create','new','A','class keyword used.','Easy'),
('Python','break statement does what?','Pauses','Exits loop','Skips iteration','Restarts','B','break exits loop.','Easy'),
('Python','Operator to check membership?','is','in','has','contains','B','in checks membership.','Easy'),

-- Medium (15)
('Python','Difference between is and ==?','No diff','is checks identity, == equality','is faster','is checks type','B','is→identity ; ==→value.','Medium'),
('Python','lambda function is?','Anonymous function','Named function','Class method','Built-in','A','lambda creates small anon fn.','Medium'),
('Python','*args means?','Multiplication','Variable arguments','Keyword args','Default args','B','*args collects variable args.','Medium'),
('Python','List comprehension is?','A loop','Concise way to make list','A function','Method','B','One-line list creation.','Medium'),
('Python','@property decorator does?','Makes static','Access as attribute','Caches','Creates var','B','Access method as attribute.','Medium'),
('Python','Purpose of __init__?','Destroys','Initializes','Copies','Compares','B','Constructor initializer.','Medium'),
('Python','enumerate() does?','Counts','Returns index & value','Sorts','Filters','B','Gives (index,value) pairs.','Medium'),
('Python','deepcopy vs copy?','Same','deepcopy copies nested objs','copy faster','deepcopy uses memory','B','deepcopy copies nested.','Medium'),
('Python','Decorator is?','Fn modifies another','A comment','Variable','Loop','A','Decorators wrap functions.','Medium'),
('Python','map() does?','Creates map','Applies fn to each','Filters','Sorts','B','Applies fn to iterable.','Medium'),
('Python','__str__ purpose?','String conversion','Concatenation','Length','Search','A','Defines printable str.','Medium'),
('Python','with statement does?','Creates context','Manages resources','Loop','Define fn','B','Auto resource cleanup.','Medium'),
('Python','Slicing means?','Cut strings','Extract sequence parts','Split','Join','B','[start:stop:step] slice.','Medium'),
('Python','zip() does?','Compress','Combine iterables','Filter','Sort','B','Combine multiple iterables.','Medium'),
('Python','GIL is?','Security','Mutex blocking multi-thread exec','Optimization','Memory mgr','B','Allows one thread at a time.','Medium'),

-- Hard (10)
('Python','Metaclass is?','Parent','Class of classes','Abstract','Interface','B','Metaclass creates classes.','Hard'),
('Python','@staticmethod does?','Class-specific','Access w/o instance','Caches','Private','B','No self/class args.','Hard'),
('Python','Monkey patching?','Fix bug','Modify at runtime','Testing','Debugging','B','Runtime modification.','Hard'),
('Python','@classmethod vs @staticmethod?','None','classmethod gets cls, static gets none','classmethod faster','static newer','B','cls vs no param.','Hard'),
('Python','__call__ does?','Calls fn','Makes instance callable','Returns','Init','B','Instance acts like fn.','Hard'),
('Python','__slots__ used for?','Define slots','Restrict attrs','Create props','Define methods','B','Saves memory.','Hard'),
('Python','Context manager?','State mgr','Resource protocol','Error handler','Memory','B','Uses __enter__/__exit__.','Hard'),
('Python','@abstractmethod does?','Static','Must implement','Optimize','Cache','B','Force subclass impl.','Hard'),
('Python','__new__ vs __init__?','None','__new__ creates obj, __init__ initializes','__new__ old','__init__ fast','B','create vs init.','Hard'),
('Python','__getattr__ purpose?','Gets','Called if attr missing','Sets','Deletes','B','Called on missing attrs.','Hard');
