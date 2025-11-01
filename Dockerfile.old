# Use Node.js 18
FROM node:18-alpine

# Set working directory
WORKDIR /app

# Copy package files
COPY package*.json ./

# Install dependencies
RUN npm install

# Copy source code
COPY . .

# Build the app
RUN npm run build

# Install serve globally
RUN npm install -g serve

# Expose port
EXPOSE $PORT

# Start the application
CMD npx serve dist -s -p $PORT