USE smartcareer;

INSERT INTO questions
(subject, question_text, option_a, option_b, option_c, option_d, correct_option, explanation, difficulty)
VALUES
-- Easy (10)
('Aptitude','What is 25% of 200?','25','50','75','100','B','25% of 200 = 50.','Easy'),
('Aptitude','If x=10, 2x+5=?','15','20','25','30','C','2×10+5=25.','Easy'),
('Aptitude','Simplify: 9×9=?','18','81','99','72','B','9×9=81.','Easy'),
('Aptitude','Average of 4,6,8=?','6','7','8','9','B','Sum 18/3=6.','Easy'),
('Aptitude','Ratio of 2:4 simplified?','1:2','2:3','3:2','2:1','A','Divide both by 2.','Easy'),
('Aptitude','Square root of 144?','10','12','14','16','B','12×12=144.','Easy'),
('Aptitude','Speed=Distance/Time. If Distance=100km, Time=2hr, Speed=?','25','50','100','200','B','100/2=50km/hr.','Easy'),
('Aptitude','Find missing: 2,4,6,__,10','7','8','9','11','B','Even number sequence.','Easy'),
('Aptitude','Sum of first 10 natural numbers?','45','50','55','60','C','n(n+1)/2=55.','Easy'),
('Aptitude','Simplify: 15% of 80','8','10','12','15','B','0.15×80=12.','Easy'),

-- Medium (12)
('Aptitude','A car runs 120 km in 2 hrs. Speed=?','50','55','60','65','C','120/2=60 km/h.','Medium'),
('Aptitude','Simple interest on ₹1000 at 10% for 2 yrs?','100','150','200','250','C','1000×10×2/100=200.','Medium'),
('Aptitude','Compound interest on ₹1000 at 10% 1 yr?','90','100','110','120','B','1000×1.1=1100 → 100 interest.','Medium'),
('Aptitude','Profit % if CP=100, SP=120','10%','15%','20%','25%','C','(20/100)×100=20%.','Medium'),
('Aptitude','Area of rectangle 10×5=?','25','40','50','60','C','10×5=50.','Medium'),
('Aptitude','Perimeter of square side 6?','12','18','24','36','C','4×6=24.','Medium'),
('Aptitude','Train speed 60km/h covers 180km in?','2h','3h','4h','5h','B','180/60=3h.','Medium'),
('Aptitude','A:B=2:3, B:C=4:5. A:C=?','2:5','8:15','3:5','4:5','B','A:C=8:15.','Medium'),
('Aptitude','If 40% of x=20, x=?','25','40','50','60','C','x=20×100/40=50.','Medium'),
('Aptitude','Find missing: 3,6,12,24,__','36','48','50','60','B','×2 pattern.','Medium'),
('Aptitude','Mean of 5,10,15,20,25','10','15','20','25','B','Sum 75/5=15.','Medium'),
('Aptitude','A man buys ₹1000, sells ₹1200, profit%?','15','18','20','25','C','Profit 200/1000×100=20%.','Medium'),

-- Hard (8)
('Aptitude','If x³=27, find x','2','3','4','5','B','Cube root of 27=3.','Hard'),
('Aptitude','Train 120m long crosses pole in 6s, speed?','60','70','72','80','C','(120/6)=20m/s=72km/h.','Hard'),
('Aptitude','Area of circle radius 7?','144','154','308','49','B','πr²≈22/7×49=154.','Hard'),
('Aptitude','If 3x-7=11, x=?','4','5','6','7','C','3x=18→x=6.','Hard'),
('Aptitude','Compound interest on ₹1000 at 10% for 2 yrs?','200','210','220','230','B','1000×1.1²=1210→210 interest.','Hard'),
('Aptitude','LCM of 8 and 12?','12','16','24','36','C','LCM=24.','Hard'),
('Aptitude','Simplify: (3/4)÷(6/8)','0.5','1','2','3','B','= (3/4)×(8/6)=1.','Hard'),
('Aptitude','Work: A 6d, B 8d, together?','3.4','3.5','3.6','4','C','1/6+1/8=7/24→24/7=3.43d.','Hard');
