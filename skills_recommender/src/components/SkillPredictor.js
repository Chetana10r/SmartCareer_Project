// SkillPredictor.js
import React, { useState } from "react";
import axios from "axios";

const SkillPredictor = () => {
  const [domain, setDomain] = useState("IT");
  const [inputText, setInputText] = useState("");
  const [skills, setSkills] = useState([]);

  const handlePredict = async () => {
    const endpoint = domain === "IT" ? "/predict_skills_it" : "/predict_skills_nonit";
    const response = await axios.post(endpoint, { text: inputText });
    setSkills(response.data.skills);
  };

  return (
    <div className="p-6 max-w-xl mx-auto rounded-2xl shadow-md bg-white mt-8">
      <h2 className="text-xl font-semibold mb-4">Skill Predictor ({domain})</h2>
      <textarea
        rows="5"
        className="w-full p-3 border rounded-md"
        placeholder="Paste your resume or keywords..."
        value={inputText}
        onChange={(e) => setInputText(e.target.value)}
      />
      <div className="flex justify-between mt-4">
        <button
          onClick={() => setDomain("IT")}
          className={`px-4 py-2 rounded-md ${domain === "IT" ? "bg-blue-600 text-white" : "bg-gray-200"}`}
        >
          IT
        </button>
        <button
          onClick={() => setDomain("Non-IT")}
          className={`px-4 py-2 rounded-md ${domain === "Non-IT" ? "bg-blue-600 text-white" : "bg-gray-200"}`}
        >
          Non-IT
        </button>
        <button
          onClick={handlePredict}
          className="bg-green-500 text-white px-6 py-2 rounded-md hover:bg-green-600"
        >
          Predict Skills
        </button>
      </div>
      <div className="mt-4">
        <h4 className="font-medium">Predicted Skills:</h4>
        <ul className="list-disc list-inside text-sm text-gray-700">
          {skills.map((skill, i) => (
            <li key={i}>{skill}</li>
          ))}
        </ul>
      </div>
    </div>
  );
};

export default SkillPredictor;
