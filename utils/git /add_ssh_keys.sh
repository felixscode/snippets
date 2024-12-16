#!/bin/bash

# Generate a new SSH key pair
read -p "Enter your email for SSH key generation: " email
read -p "Enter your GitHub username: " username
ssh-keygen -t rsa -b 4096 -C "$email" -f ~/.ssh/$username -N ""

# Start the ssh-agent in the background
eval "$(ssh-agent -s)"

# Add the new SSH private key to the ssh-agent
ssh-add ~/.ssh/$username

# Display the public key
echo "Your new SSH public key is:"
cat ~/.ssh/$username.pub

# Check the local SSH agent
ssh-add -l