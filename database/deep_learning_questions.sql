USE smartcareer;

INSERT INTO questions (subject,question_text,option_a,option_b,option_c,option_d,correct_option,explanation,difficulty)
VALUES
-- Easy (10)
('Deep Learning','Deep Learning is a subset of?','AI','Data Science','Machine Learning','Statistics','C','Subset of ML.','Easy'),
('Deep Learning','Main library for DL in Python?','scikit-learn','TensorFlow','NumPy','Matplotlib','B','TensorFlow for DL.','Easy'),
('Deep Learning','Neuron activation function introduces?','Linearity','Non-linearity','Memory','Speed','B','Non-linearity.','Easy'),
('Deep Learning','Which layer extracts features in CNN?','Pooling','Convolution','Dense','Dropout','B','Conv layer extracts.','Easy'),
('Deep Learning','RNN used for?','Images','Sequential data','Tabular','Graphs','B','For sequences.','Easy'),
('Deep Learning','Dropout is used for?','Training','Regularization','Loss','Feature engg','B','Prevents overfitting.','Easy'),
('Deep Learning','Backpropagation updates?','Inputs','Weights','Bias only','Outputs','B','Updates weights.','Easy'),
('Deep Learning','ReLU stands for?','Rectified Linear Unit','Regular Linear Util','Reduced LU','Random LU','A','Most common activation.','Easy'),
('Deep Learning','Epoch means?','1 iteration over data','Half epoch','Step','Batch','A','One full pass.','Easy'),
('Deep Learning','Loss function for classification?','MSE','Cross Entropy','MAE','Huber','B','Cross-entropy loss.','Easy'),

-- Medium (12)
('Deep Learning','Vanishing gradient happens when?','Weights too large','Gradients → 0','Bias zero','Data missing','B','Gradients shrink.','Medium'),
('Deep Learning','Batch Normalization does?','Normalize inputs','Normalize activations','Regularize data','Increase loss','B','Normalizes layer output.','Medium'),
('Deep Learning','Optimizer Adam combines?','SGD + Momentum','RMSProp + Momentum','Adagrad + RMSProp','SGD + Adagrad','C','Adam = Adagrad + RMSProp.','Medium'),
('Deep Learning','CNN uses what operation?','Matrix add','Convolution','Pooling','Activation','B','Convolution filters.','Medium'),
('Deep Learning','LSTM solves which problem?','Overfit','Vanishing gradient','Low accuracy','Noise','B','Uses gates.','Medium'),
('Deep Learning','Transfer Learning means?','Train from scratch','Reuse pre-trained model','Randomize','Augment','B','Reuse knowledge.','Medium'),
('Deep Learning','Softmax outputs?','Binary','Probabilities','Weights','Loss','B','Probability vector.','Medium'),
('Deep Learning','Pooling layer reduces?','Resolution','Weights','Data','Labels','A','Down-samples feature map.','Medium'),
('Deep Learning','Gradient Explosion caused by?','Small lr','Large lr','Big gradients','Low batch','C','Too large gradients.','Medium'),
('Deep Learning','Autoencoder used for?','Regression','Feature learning','Classification','Visualization','B','Learns representation.','Medium'),
('Deep Learning','GAN has two nets?','Classifier-Regressor','Generator-Discriminator','Encoder-Decoder','Actor-Critic','B','Two competing nets.','Medium'),
('Deep Learning','Parameter sharing in CNN means?','Same weights used','Unique weights','Shared data','Shared output','A','Reduces params.','Medium'),

-- Hard (8)
('Deep Learning','Gradient clipping used for?','Prevent explosion','Speed','Regularization','Normalization','A','Limits grad value.','Hard'),
('Deep Learning','Batch size affects?','Memory & generalization','Nothing','Loss fn','Optimizer','A','Trade-off accuracy vs speed.','Hard'),
('Deep Learning','Attention mechanism improves?','Image quality','Focus on important parts','Speed','Memory','B','Weights relevant features.','Hard'),
('Deep Learning','Transformer model based on?','CNN','RNN','Self-attention','Autoencoder','C','Self-attention.','Hard'),
('Deep Learning','BERT stands for?','Bidirectional Encoder Representations from Transformers','Basic Encoder Regression Transformer','Binary Encoding Recurrent Transformer','None','A','BERT model.','Hard'),
('Deep Learning','Activation tanh range?','0-1','-1 to 1','0-∞','-∞ to ∞','B','tanh → -1 to 1.','Hard'),
('Deep Learning','Weight initialization important for?','Speed only','Convergence & stability','Memory','Accuracy only','B','Prevents grad issues.','Hard'),
('Deep Learning','Learning rate schedule helps?','Increase error','Faster & stable training','Reduce data','Fix 0 grads','B','Dynamic lr improves training.','Hard');
