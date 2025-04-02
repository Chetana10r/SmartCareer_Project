import React from 'react';

const SkillRecommendation = ({ skills }) => {
    return (
        <div>
            <h3>Recommended Skills:</h3>
            <ul>
                {skills.map((skill, index) => (
                    <li key={index}>{skill}</li>
                ))}
            </ul>
        </div>
    );
};

export default SkillRecommendation;

