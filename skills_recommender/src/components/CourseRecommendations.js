import React, { useEffect, useState } from "react";
import "./CourseRecommendations.css";

function CourseRecommendations({ courseQuery }) {
  const [courses, setCourses] = useState([]);

  useEffect(() => {
    // Mocked course data - you can replace this with real API integration
    const mockCourses = [
      {
        title: `Beginner ${courseQuery} Course`,
        provider: "Coursera",
        link: "https://www.coursera.org/search?query=" + courseQuery,
      },
      {
        title: `Advanced ${courseQuery} Specialization`,
        provider: "edX",
        link: "https://www.edx.org/search?q=" + courseQuery,
      },
      {
        title: `Crash Course on ${courseQuery}`,
        provider: "Udemy",
        link: "https://www.udemy.com/courses/search/?q=" + courseQuery,
      },
      {
        title: `${courseQuery} for Data Science`,
        provider: "YouTube (free)",
        link: "https://www.youtube.com/results?search_query=" + courseQuery + "+course",
      },
    ];
    setCourses(mockCourses);
  }, [courseQuery]);

  return (
    <div className="course-recommendations-container">
      <h2>📚 Recommended Free Courses on {courseQuery}</h2>
      <div className="course-card-container">
        {courses.map((course, index) => (
          <div className="course-card" key={index}>
            <h4>{course.title}</h4>
            <p>Provider: {course.provider}</p>
            <a href={course.link} target="_blank" rel="noopener noreferrer">
              🔗 Go to Course
            </a>
          </div>
        ))}
      </div>
    </div>
  );
}

export default CourseRecommendations;
