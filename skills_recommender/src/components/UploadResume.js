import React, { useState } from 'react';

const UploadResume = ({ setSkills }) => {
    const [file, setFile] = useState(null);
    const [loading, setLoading] = useState(false);
    const [message, setMessage] = useState("");

    const handleUpload = async () => {
        if (!file) {
            alert("Please upload a resume file");
            return;
        }

        const allowedExtensions = ['pdf', 'doc', 'docx', 'txt'];
        const fileExtension = file.name.split('.').pop().toLowerCase();

        if (!allowedExtensions.includes(fileExtension)) {
            alert("Unsupported file format. Only PDF, DOC, DOCX, and TXT files are allowed.");
            return;
        }

        setLoading(true);
        setMessage("");

        const formData = new FormData();
        formData.append("resume", file);

        try {
            const response = await fetch("http://localhost:5000/upload_resume", {
                method: "POST",
                body: formData,
            });

            if (!response.ok) {
                throw new Error("Failed to upload resume");
            }

            const data = await response.json();
            setSkills(data.resume_text || "No skills extracted");
            setMessage("Resume uploaded successfully!");
        } catch (error) {
            console.error("Error uploading resume:", error);
            alert("Error uploading resume. Please try again.");
        } finally {
            setLoading(false);
        }
    };

    return (
        <div>
            <input type="file" onChange={(e) => setFile(e.target.files[0])} />
            <button onClick={handleUpload} disabled={loading}>
                {loading ? "Uploading..." : "Upload Resume"}
            </button>
            {message && <p>{message}</p>}
        </div>
    );
};

export default UploadResume;
