import React, { useState } from 'react';

const JobRoleSuggestions = ({ skills }) => {
    const [roles, setRoles] = useState([]);

    const fetchRoles = async () => {
        const response = await fetch("http://localhost:5000/suggest_roles", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ skills }),
        });

        const data = await response.json();
        setRoles(data.roles);
    };

    return (
        <div>
            <button onClick={fetchRoles}>Suggest Job Roles</button>
            <ul>
                {roles.map((role, index) => (
                    <li key={index}>{role}</li>
                ))}
            </ul>
        </div>
    );
};

export default JobRoleSuggestions;
