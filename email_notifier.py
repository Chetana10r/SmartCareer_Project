import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import Dict
import os

class EmailNotifier:
    def __init__(self):
        """Initialize email notifier with SMTP settings"""
        self.smtp_server = os.getenv('SMTP_SERVER', 'smtp.gmail.com')
        self.smtp_port = int(os.getenv('SMTP_PORT', '587'))
        self.sender_email = os.getenv('SENDER_EMAIL', '')
        self.sender_password = os.getenv('SENDER_PASSWORD', '')
        self.enabled = bool(self.sender_email and self.sender_password)
        
        if not self.enabled:
            print("Email notifications disabled. Set SMTP credentials in environment variables.")
    
    def send_shortlist_email(self, candidate: Dict, job: Dict) -> bool:
        """
        Send shortlist notification to candidate
        
        Args:
            candidate: Candidate details
            job: Job details
        
        Returns:
            Success status
        """
        if not self.enabled:
            print("Email notifications are disabled")
            return False
        
        try:
            candidate_email = candidate.get('email', '')
            candidate_name = candidate.get('name', 'Candidate')
            
            if not candidate_email:
                print("Candidate email not found")
                return False
            
            subject = f"Congratulations! You've been shortlisted for {job.get('title')}"
            body = self._generate_shortlist_email_body(candidate_name, job)
            
            return self._send_email(candidate_email, subject, body)
            
        except Exception as e:
            print(f"Error sending shortlist email: {e}")
            return False
    
    def send_interview_invitation(self, candidate: Dict, job: Dict, interview_details: Dict) -> bool:
        """Send interview invitation to candidate"""
        if not self.enabled:
            return False
        
        try:
            candidate_email = candidate.get('email', '')
            candidate_name = candidate.get('name', 'Candidate')
            
            if not candidate_email:
                return False
            
            subject = f"Interview Invitation - {job.get('title')} at {job.get('company')}"
            body = self._generate_interview_email_body(candidate_name, job, interview_details)
            
            return self._send_email(candidate_email, subject, body)
            
        except Exception as e:
            print(f"Error sending interview email: {e}")
            return False
    
    def send_rejection_email(self, candidate: Dict, job: Dict) -> bool:
        """Send rejection notification to candidate"""
        if not self.enabled:
            return False
        
        try:
            candidate_email = candidate.get('email', '')
            candidate_name = candidate.get('name', 'Candidate')
            
            if not candidate_email:
                return False
            
            subject = f"Update on your application - {job.get('title')}"
            body = self._generate_rejection_email_body(candidate_name, job)
            
            return self._send_email(candidate_email, subject, body)
            
        except Exception as e:
            print(f"Error sending rejection email: {e}")
            return False
    
    def send_selection_email(self, candidate: Dict, job: Dict) -> bool:
        """Send selection/offer notification"""
        if not self.enabled:
            return False
        
        try:
            candidate_email = candidate.get('email', '')
            candidate_name = candidate.get('name', 'Candidate')
            
            if not candidate_email:
                return False
            
            subject = f"🎉 Congratulations! Job Offer - {job.get('title')}"
            body = self._generate_selection_email_body(candidate_name, job)
            
            return self._send_email(candidate_email, subject, body)
            
        except Exception as e:
            print(f"Error sending selection email: {e}")
            return False
    
    def _send_email(self, recipient_email: str, subject: str, body: str) -> bool:
        """Send email using SMTP"""
        try:
            # Create message
            message = MIMEMultipart('alternative')
            message['Subject'] = subject
            message['From'] = self.sender_email
            message['To'] = recipient_email
            
            # Add HTML body
            html_part = MIMEText(body, 'html')
            message.attach(html_part)
            
            # Connect to SMTP server
            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                server.starttls()
                server.login(self.sender_email, self.sender_password)
                server.send_message(message)
            
            print(f"Email sent successfully to {recipient_email}")
            return True
            
        except Exception as e:
            print(f"Error sending email: {e}")
            return False
    
    def _generate_shortlist_email_body(self, candidate_name: str, job: Dict) -> str:
        """Generate HTML email body for shortlist notification"""
        return f"""
        <!DOCTYPE html>
        <html>
        <head>
            <style>
                body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
                .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                .header {{ background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
                           color: white; padding: 30px; text-align: center; border-radius: 10px 10px 0 0; }}
                .content {{ background: #f9f9f9; padding: 30px; border-radius: 0 0 10px 10px; }}
                .job-details {{ background: white; padding: 20px; margin: 20px 0; border-radius: 8px; 
                               border-left: 4px solid #667eea; }}
                .footer {{ text-align: center; padding: 20px; color: #666; font-size: 12px; }}
                .button {{ display: inline-block; padding: 12px 30px; background: #667eea; 
                          color: white; text-decoration: none; border-radius: 5px; margin: 20px 0; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>🎉 Congratulations!</h1>
                </div>
                <div class="content">
                    <p>Dear {candidate_name},</p>
                    
                    <p>We're excited to inform you that you've been <strong>shortlisted</strong> for the following position:</p>
                    
                    <div class="job-details">
                        <h2>{job.get('title', 'Job Position')}</h2>
                        <p><strong>Company:</strong> {job.get('company', 'N/A')}</p>
                        <p><strong>Location:</strong> {job.get('location', 'N/A')}</p>
                        <p><strong>Type:</strong> {job.get('type', 'Full-time')}</p>
                    </div>
                    
                    <p>Your profile stood out among many applicants, and we believe you have the skills 
                    and experience we're looking for.</p>
                    
                    <p><strong>Next Steps:</strong></p>
                    <ul>
                        <li>Our recruitment team will review your profile in detail</li>
                        <li>You will be contacted shortly for the next round</li>
                        <li>Keep an eye on your email for further updates</li>
                    </ul>
                    
                    <p>We look forward to connecting with you soon!</p>
                    
                    <p>Best regards,<br>
                    <strong>The Recruitment Team</strong></p>
                </div>
                <div class="footer">
                    <p>This is an automated notification from SmartCareer Platform</p>
                </div>
            </div>
        </body>
        </html>
        """
    
    def _generate_interview_email_body(self, candidate_name: str, job: Dict, interview_details: Dict) -> str:
        """Generate HTML email body for interview invitation"""
        return f"""
        <!DOCTYPE html>
        <html>
        <head>
            <style>
                body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
                .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                .header {{ background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
                           color: white; padding: 30px; text-align: center; border-radius: 10px 10px 0 0; }}
                .content {{ background: #f9f9f9; padding: 30px; border-radius: 0 0 10px 10px; }}
                .interview-box {{ background: white; padding: 20px; margin: 20px 0; border-radius: 8px; 
                                 border: 2px solid #667eea; }}
                .highlight {{ background: #fff3cd; padding: 10px; border-radius: 5px; margin: 10px 0; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>📅 Interview Invitation</h1>
                </div>
                <div class="content">
                    <p>Dear {candidate_name},</p>
                    
                    <p>Congratulations! We would like to invite you for an interview for the position of 
                    <strong>{job.get('title')}</strong> at <strong>{job.get('company')}</strong>.</p>
                    
                    <div class="interview-box">
                        <h3>Interview Details</h3>
                        <p><strong>Date:</strong> {interview_details.get('date', 'TBD')}</p>
                        <p><strong>Time:</strong> {interview_details.get('time', 'TBD')}</p>
                        <p><strong>Duration:</strong> {interview_details.get('duration', '45-60 minutes')}</p>
                        <p><strong>Mode:</strong> {interview_details.get('mode', 'Video Call')}</p>
                        <p><strong>Meeting Link:</strong> {interview_details.get('link', 'Will be shared separately')}</p>
                    </div>
                    
                    <div class="highlight">
                        <strong>⚠️ Important:</strong> Please confirm your availability by replying to this email.
                    </div>
                    
                    <p><strong>Preparation Tips:</strong></p>
                    <ul>
                        <li>Review the job description carefully</li>
                        <li>Prepare examples of your relevant experience</li>
                        <li>Test your video/audio setup beforehand</li>
                        <li>Keep your resume handy</li>
                    </ul>
                    
                    <p>We look forward to meeting you!</p>
                    
                    <p>Best regards,<br>
                    <strong>{job.get('company')} Recruitment Team</strong></p>
                </div>
            </div>
        </body>
        </html>
        """
    
    def _generate_rejection_email_body(self, candidate_name: str, job: Dict) -> str:
        """Generate HTML email body for rejection notification"""
        return f"""
        <!DOCTYPE html>
        <html>
        <head>
            <style>
                body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
                .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                .header {{ background: #6c757d; color: white; padding: 30px; 
                          text-align: center; border-radius: 10px 10px 0 0; }}
                .content {{ background: #f9f9f9; padding: 30px; border-radius: 0 0 10px 10px; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>Application Update</h1>
                </div>
                <div class="content">
                    <p>Dear {candidate_name},</p>
                    
                    <p>Thank you for your interest in the <strong>{job.get('title')}</strong> 
                    position at <strong>{job.get('company')}</strong>.</p>
                    
                    <p>After careful consideration, we regret to inform you that we have decided to move 
                    forward with other candidates whose qualifications more closely match our current needs.</p>
                    
                    <p>We were impressed by your background and encourage you to apply for other positions 
                    that match your skills and interests.</p>
                    
                    <p>We wish you all the best in your job search and future career endeavors.</p>
                    
                    <p>Best regards,<br>
                    <strong>{job.get('company')} Recruitment Team</strong></p>
                </div>
            </div>
        </body>
        </html>
        """
    
    def _generate_selection_email_body(self, candidate_name: str, job: Dict) -> str:
        """Generate HTML email body for selection notification"""
        return f"""
        <!DOCTYPE html>
        <html>
        <head>
            <style>
                body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
                .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                .header {{ background: linear-gradient(135deg, #11998e 0%, #38ef7d 100%); 
                          color: white; padding: 40px; text-align: center; border-radius: 10px 10px 0 0; }}
                .content {{ background: #f9f9f9; padding: 30px; border-radius: 0 0 10px 10px; }}
                .celebration {{ font-size: 48px; text-align: center; margin: 20px 0; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>🎊 Congratulations! 🎊</h1>
                    <h2>You've Been Selected!</h2>
                </div>
                <div class="content">
                    <div class="celebration">🎉 🎉 🎉</div>
                    
                    <p>Dear {candidate_name},</p>
                    
                    <p>We are thrilled to extend you an offer for the position of 
                    <strong>{job.get('title')}</strong> at <strong>{job.get('company')}</strong>!</p>
                    
                    <p>Your skills, experience, and enthusiasm impressed us throughout the interview process, 
                    and we believe you will be a valuable addition to our team.</p>
                    
                    <p><strong>Next Steps:</strong></p>
                    <ul>
                        <li>Our HR team will contact you with the formal offer letter</li>
                        <li>Review the offer details and compensation package</li>
                        <li>Complete the necessary documentation</li>
                        <li>Discuss the joining date</li>
                    </ul>
                    
                    <p>We're excited to have you join our team!</p>
                    
                    <p>Warmest regards,<br>
                    <strong>{job.get('company')} Recruitment Team</strong></p>
                </div>
            </div>
        </body>
        </html>
        """