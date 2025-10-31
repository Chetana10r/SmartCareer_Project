USE smartcareer;

INSERT INTO questions
(subject, question_text, option_a, option_b, option_c, option_d, correct_option, explanation, difficulty)
VALUES
-- Easy (10)
('Machine Learning','ML stands for what?','Matrix Logic','Machine Learning','Meta Language','Main Loop','B','ML = Machine Learning.','Easy'),
('Machine Learning','Supervised learning needs?','Labels','Unlabeled data','No data','Rules','A','Uses labeled data.','Easy'),
('Machine Learning','Algorithm for classification?','K-Means','Linear Regression','Decision Tree','Apriori','C','Decision Tree classifies.','Easy'),
('Machine Learning','Which library is used for ML in Python?','NumPy','Matplotlib','scikit-learn','Pandas','C','scikit-learn for ML.','Easy'),
('Machine Learning','Regression predicts?','Categories','Continuous values','Clusters','Labels','B','Regression → continuous.','Easy'),
('Machine Learning','Train-test split is used for?','Visualization','Validation','Saving','Deployment','B','To evaluate model.','Easy'),
('Machine Learning','Overfitting means?','Good fit','Too complex','Underfit','Random','B','Model fits noise.','Easy'),
('Machine Learning','KNN stands for?','K-Nearest Neighbor','Kernel Network','Key Node Net','Known Num Net','A','K-Nearest Neighbor.','Easy'),
('Machine Learning','Which is ensemble method?','SVM','Random Forest','Naive Bayes','K-Means','B','Random Forest = ensemble.','Easy'),
('Machine Learning','Loss function measures?','Accuracy','Error','Speed','Data size','B','Loss = error.','Easy'),

-- Medium (12)
('Machine Learning','Feature scaling used because?','Reduce dim','Normalize values','Remove cols','Encode text','B','Keeps features comparable.','Medium'),
('Machine Learning','Which reduces dimensionality?','PCA','SVM','KNN','Naive Bayes','A','PCA reduces dimensions.','Medium'),
('Machine Learning','Gradient Descent does what?','Minimizes loss','Maximizes loss','Sorts','Splits','A','Optimizes parameters.','Medium'),
('Machine Learning','Bias-variance trade-off concerns?','Memory','Generalization','Data type','Syntax','B','Balance fit vs gen.','Medium'),
('Machine Learning','Cross validation purpose?','Speed','Model evaluation','Data merge','Feature sel','B','Ensures robust testing.','Medium'),
('Machine Learning','Naive Bayes assumes?','Features dependent','Features independent','Linear','Tree','B','Assumes independence.','Medium'),
('Machine Learning','Logistic regression output?','Continuous','Binary','Cluster','Tree','B','Binary classification.','Medium'),
('Machine Learning','Regularization prevents?','Scaling','Overfitting','Underfitting','Missing data','B','Adds penalty.','Medium'),
('Machine Learning','R² score represents?','Error','Goodness of fit','Speed','Loss','B','Higher R² → better.','Medium'),
('Machine Learning','Random Forest built from?','Neurons','Trees','Lines','Graphs','B','Ensemble of trees.','Medium'),
('Machine Learning','SVM tries to?','Maximize margin','Minimize margin','Reduce bias','Add noise','A','Max margin classifier.','Medium'),
('Machine Learning','Confusion matrix shows?','Errors only','TP FP TN FN','Accuracy','Loss','B','All prediction cases.','Medium'),

-- Hard (8)
('Machine Learning','Gradient Descent may get stuck in?','Optimum','Local minima','Global min','Origin','B','Local minima problem.','Hard'),
('Machine Learning','L1 regularization adds?','Sum of abs','Sum of squares','None','Mean','A','L1 adds |w|.','Hard'),
('Machine Learning','Kernel trick used in?','SVM','KNN','Tree','LR','A','SVM kernel maps space.','Hard'),
('Machine Learning','ROC curve plots?','Precision-Recall','TPR vs FPR','Loss vs Epoch','R² vs Error','B','TPR vs FPR.','Hard'),
('Machine Learning','Bagging vs Boosting diff?','Seq vs Parallel','Parallel vs Seq','None','Swap','B','Boosting = seq; bagging = parallel.','Hard'),
('Machine Learning','Hyperparameter tuning done via?','Cross-val','Grid Search','Gradient','PCA','B','Grid Search CV.','Hard'),
('Machine Learning','Early stopping used for?','Speed','Avoid overfit','Reduce data','Normalize','B','Stops when val loss ↑.','Hard'),
('Machine Learning','Feature importance helps in?','Overfit','Interpretability','Normalization','Dim reduce','B','Shows influence of features.','Hard');
