// const express = require('express');
// const bodyParser = require('body-parser');
// const { GoogleGenerativeAI } = require('@google/generative-ai');

// const app = express();
// app.use(bodyParser.json());
// app.use(express.static('public')); // Serve your HTML/CSS/JS files

// const GOOGLE_API_KEY = "AIzaSyCJlefBe70vjVMPIAQvjyfJLDa6T_FfWRc";
// const genAI = new GoogleGenerativeAI(GOOGLE_API_KEY);

// app.post('/chat', async (req, res) => {
//     try {
//         const userMessage = req.body.message;
        
//         // Initialize the model
//         const model = genAI.getGenerativeModel({ model: "gemini-pro" });
        
//         // Start a chat session
//         const chat = model.startChat();
        
//         // Get response from Gemini
//         const result = await chat.sendMessage(userMessage);
//         const response = await result.response;
        
//         res.json({ response: response.text() });
//     } catch (error) {
//         console.error('Error:', error);
//         res.status(500).json({ error: 'An error occurred' });
//     }
// });

// app.listen(8080, () => {
//     console.log('Server is running on port 8080');
// });
