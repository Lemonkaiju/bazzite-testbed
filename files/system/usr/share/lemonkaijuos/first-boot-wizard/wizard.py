#!/usr/bin/env python3
"""
LemonKaijuOS First-Boot Wizard
Multi-user setup, STFD integration, and app selection
"""

from flask import Flask, render_template, request, jsonify, redirect, url_for
import subprocess
import json
import os
import yaml
from pathlib import Path

app = Flask(__name__)
app.secret_key = os.urandom(24)

# Configuration
WIZARD_DATA_DIR = Path("/var/lib/lemonkaijuos/wizard")
WIZARD_DATA_DIR.mkdir(parents=True, exist_ok=True)

# App categories and profiles
APP_CATEGORIES = yaml.safe_load(open('data/app_categories.yaml'))
USER_PROFILES = yaml.safe_load(open('data/user_profiles.yaml'))

# Wizard state
wizard_state = {
    'step': 1,
    'users': [],
    'stfd_enabled': False,
    'stfd_credentials': {},
    'ai_permissions': {},
    'selected_apps': [],
    'selected_profile': 'custom'
}


@app.route('/')
def index():
    """Welcome screen"""
    return render_template('welcome.html')


@app.route('/step/<int:step_num>')
def step(step_num):
    """Render wizard step"""
    wizard_state['step'] = step_num
    
    templates = {
        1: 'step1_users.html',
        2: 'step2_stfd.html',
        3: 'step3_ai_permissions.html',
        4: 'step4_app_selection.html',
        5: 'step5_app_customization.html',
        6: 'step6_ai_assistant.html',
        7: 'step7_review.html',
        8: 'step8_installation.html'
    }
    
    template = templates.get(step_num, 'welcome.html')
    return render_template(template, state=wizard_state, 
                         categories=APP_CATEGORIES,
                         profiles=USER_PROFILES)


@app.route('/api/users', methods=['POST'])
def save_users():
    """Save user account information"""
    data = request.json
    wizard_state['users'] = data.get('users', [])
    return jsonify({'success': True})


@app.route('/api/stfd', methods=['POST'])
def save_stfd():
    """Save STFD integration settings"""
    data = request.json
    wizard_state['stfd_enabled'] = data.get('enabled', False)
    wizard_state['stfd_credentials'] = data.get('credentials', {})
    return jsonify({'success': True})


@app.route('/api/ai-permissions', methods=['POST'])
def save_ai_permissions():
    """Save AI management permissions"""
    data = request.json
    wizard_state['ai_permissions'] = data.get('permissions', {})
    return jsonify({'success': True})


@app.route('/api/apps', methods=['POST'])
def save_apps():
    """Save selected applications"""
    data = request.json
    wizard_state['selected_profile'] = data.get('profile', 'custom')
    wizard_state['selected_apps'] = data.get('apps', [])
    return jsonify({'success': True})


@app.route('/api/install', methods=['POST'])
def install():
    """Execute installation based on wizard choices"""
    try:
        # Create user accounts
        create_users(wizard_state['users'])
        
        # Configure STFD integration if enabled
        if wizard_state['stfd_enabled']:
            configure_stfd(wizard_state['stfd_credentials'])
            configure_ai_permissions(wizard_state['ai_permissions'])
        
        # Install selected applications
        install_applications(wizard_state['selected_apps'])
        
        # Configure AI assistant if requested
        if wizard_state['ai_permissions'].get('ollama_enabled'):
            install_ollama()
        
        return jsonify({'success': True, 'message': 'Installation complete!'})
    
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


def create_users(users):
    """Create user accounts with appropriate permissions"""
    for user in users:
        username = user['username']
        password = user['password']
        role = user['role']
        
        # Create user
        subprocess.run(['useradd', '-m', '-s', '/bin/bash', username], check=True)
        
        # Set password
        proc = subprocess.Popen(['passwd', username], stdin=subprocess.PIPE)
        proc.communicate(f"{password}\n{password}\n".encode())
        
        # Add to appropriate groups based on role
        if role == 'administrator':
            subprocess.run(['usermod', '-aG', 'wheel,sudo,flatpak-admin', username], check=True)
        elif role == 'family':
            subprocess.run(['usermod', '-aG', 'flatpak-user', username], check=True)
        elif role == 'child':
            # Restricted groups, configure PAM for time limits
            configure_child_account(username)
        # Guest accounts handled separately


def configure_stfd(credentials):
    """Configure STFD integration"""
    config = {
        'network_name': credentials.get('network_name'),
        'admin_username': credentials.get('admin_username'),
        'admin_password': credentials.get('admin_password')
    }
    
    config_file = Path('/etc/lemonkaijuos/stfd-config.json')
    config_file.parent.mkdir(parents=True, exist_ok=True)
    config_file.write_text(json.dumps(config, indent=2))
    
    # Enable SSH for admin access
    subprocess.run(['systemctl', 'enable', 'sshd'], check=True)


def configure_ai_permissions(permissions):
    """Configure AI facilitator permissions"""
    config = {
        'auto_security_updates': permissions.get('auto_security_updates', True),
        'system_monitoring': permissions.get('system_monitoring', True),
        'auto_app_updates': permissions.get('auto_app_updates', False),
        'remote_troubleshooting': permissions.get('remote_troubleshooting', False)
    }
    
    config_file = Path('/etc/lemonkaijuos/ai-permissions.json')
    config_file.parent.mkdir(parents=True, exist_ok=True)
    config_file.write_text(json.dumps(config, indent=2))


def install_applications(apps):
    """Install selected flatpak applications"""
    for app_id in apps:
        try:
            subprocess.run(['flatpak', 'install', '-y', 'flathub', app_id], 
                         check=True, capture_output=True)
        except subprocess.CalledProcessError as e:
            print(f"Failed to install {app_id}: {e}")


def install_ollama():
    """Install Ollama and download AI model"""
    # Download and install Ollama
    subprocess.run(['curl', '-fsSL', 'https://ollama.com/install.sh'], 
                  stdout=subprocess.PIPE, check=True)
    subprocess.run(['sh', '-'], stdin=subprocess.PIPE, check=True)
    
    # Pull llama3.1:8b model
    subprocess.run(['ollama', 'pull', 'llama3.1:8b'], check=True)
    
    # Configure Ollama to start on boot
    subprocess.run(['systemctl', 'enable', 'ollama'], check=True)


def configure_child_account(username):
    """Configure restrictions for child accounts"""
    # TODO: Implement PAM time limits, content filtering
    pass


if __name__ == '__main__':
    app.run(host='127.0.0.1', port=5555, debug=False)
