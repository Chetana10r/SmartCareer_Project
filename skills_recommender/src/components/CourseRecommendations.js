import React, { useState } from 'react';

const CourseRecommendations = ({ skills }) => {
    const [courses, setCourses] = useState([]);

    const fetchCourses = async () => {
        const response = await fetch("http://localhost:5000/recommend_courses", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ skills }),
        });

        const data = await response.json();
        setCourses(data.courses);
    };

    return (
        <div>
            <button onClick={fetchCourses}>Get Recommended Courses</button>
            <ul>
                {courses.map((course, index) => (
                    <li key={index}>{course}</li>
                ))}
            </ul>
        </div>
    );
};

export default CourseRecommendations;
