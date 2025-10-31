import React, { useState, useEffect } from 'react';

const Time = ({ timeLimit, onTimeUp, setTimeLimit }) => {
  const [timeLeft, setTimeLeft] = useState(timeLimit);
  const [isWarning, setIsWarning] = useState(false);

  useEffect(() => {
    if (timeLeft <= 0) {
      onTimeUp();
      return;
    }

    // Warning when 2 minutes left
    if (timeLeft <= 120 && !isWarning) {
      setIsWarning(true);
    }

    const timer = setInterval(() => {
      setTimeLeft(prev => {
        const newTime = prev - 1;
        setTimeLimit(newTime);
        return newTime;
      });
    }, 1000);

    return () => clearInterval(timer);
  }, [timeLeft, onTimeUp, isWarning, setTimeLimit]);

  const formatTime = (seconds) => {
    const mins = Math.floor(seconds / 60);
    const secs = seconds % 60;
    return `${mins.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`;
  };

  const getProgressColor = () => {
    if (timeLeft > 300) return '#4caf50'; // Green
    if (timeLeft > 120) return '#ff9800'; // Orange
    return '#f44336'; // Red
  };

  const progressPercentage = (timeLeft / timeLimit) * 100;

  return (
    <div className={`timer-container ${isWarning ? 'warning' : ''}`} style={styles.timerContainer}>
      <div className="timer-icon" style={styles.timerIcon}>
        <svg width="24" height="24" viewBox="0 0 24 24" fill="currentColor">
          <path d="M15 1H9v2h6V1zm-4 13h2V8h-2v6zm8.03-6.61l1.42-1.42c-.43-.51-.9-.99-1.41-1.41l-1.42 1.42C16.07 4.74 14.12 4 12 4c-4.97 0-9 4.03-9 9s4.02 9 9 9 9-4.03 9-9c0-2.12-.74-4.07-1.97-5.61zM12 20c-3.87 0-7-3.13-7-7s3.13-7 7-7 7 3.13 7 7-3.13 7-7 7z"/>
        </svg>
      </div>
      <div className="timer-display" style={styles.timerDisplay}>
        <div className="time-text" style={styles.timeText}>{formatTime(timeLeft)}</div>
        <div className="timer-progress" style={styles.timerProgress}>
          <div 
            className="timer-bar" 
            style={{ 
              ...styles.timerBar,
              width: `${progressPercentage}%`,
              backgroundColor: getProgressColor()
            }}
          />
        </div>
      </div>
      {isWarning && (
        <div className="timer-warning" style={styles.timerWarning}>
          ⚠️ Time running out!
        </div>
      )}
    </div>
  );
};

const styles = {
  timerContainer: {
    display: 'flex',
    alignItems: 'center',
    gap: '10px',
    background: '#f5f5f5',
    padding: '10px 20px',
    borderRadius: '8px',
  },
  timerIcon: {
    fontSize: '1.5rem',
    color: '#2196f3',
    display: 'flex',
    alignItems: 'center',
  },
  timerDisplay: {
    display: 'flex',
    flexDirection: 'column',
    gap: '5px',
  },
  timeText: {
    fontSize: '1.2rem',
    fontWeight: 'bold',
    color: '#333',
  },
  timerProgress: {
    width: '100px',
    height: '4px',
    background: '#ddd',
    borderRadius: '2px',
    overflow: 'hidden',
  },
  timerBar: {
    height: '100%',
    transition: 'width 1s linear, background-color 0.3s',
  },
  timerWarning: {
    color: '#f44336',
    fontSize: '0.8rem',
    fontWeight: 'bold',
  }
};

export default Time;