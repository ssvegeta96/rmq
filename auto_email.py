import win32com.client as win32

# Initialize Outlook application
outlook = win32.Dispatch('outlook.application')

# Open the email template
mail = outlook.CreateItemFromTemplate('C:\\path\\to\\template.oft')

# Replace placeholders in the email body
mail.Body = mail.Body.replace('{{variable_1}}', 'Value 1')
mail.Body = mail.Body.replace('{{variable_2}}', 'Value 2')

# Add recipients
mail.To = 'recipient@example.com'
mail.CC = 'cc@example.com'

# Send the email
mail.Send()
