---
name: Ansible Automation
description: Ansible best practices for playbooks, roles, inventory management, and infrastructure automation
version: 1.0.0
triggers:
  - ansible
  - playbook
  - ansible role
  - ansible galaxy
  - ansible vault
  - inventory
  - ansible tower
  - awx
---

# Ansible Automation Skill

This skill automatically activates when working with Ansible to ensure best practices for playbooks, roles, inventory management, and secure automation.

## Core Principle

**IDEMPOTENT, SECURE, MAINTAINABLE AUTOMATION**

```
❌ Ad-hoc commands, hardcoded secrets, monolithic playbooks
✅ Reusable roles, encrypted vaults, modular structure
```

## Project Structure

```
ansible/
├── ansible.cfg                 # Ansible configuration
├── inventory/
│   ├── production/
│   │   ├── hosts.yml          # Production inventory
│   │   └── group_vars/
│   │       ├── all.yml
│   │       └── webservers.yml
│   └── staging/
│       ├── hosts.yml
│       └── group_vars/
├── playbooks/
│   ├── site.yml               # Main playbook
│   ├── webservers.yml
│   └── databases.yml
├── roles/
│   ├── common/
│   ├── nginx/
│   └── postgresql/
├── collections/
│   └── requirements.yml
├── group_vars/
│   └── all/
│       ├── vars.yml
│       └── vault.yml          # Encrypted secrets
└── host_vars/
```

## Best Practice Patterns

### Playbook Structure
```yaml
# playbooks/webservers.yml
---
- name: Configure Web Servers
  hosts: webservers
  become: true
  gather_facts: true

  vars_files:
    - ../group_vars/all/vars.yml

  pre_tasks:
    - name: Update apt cache
      ansible.builtin.apt:
        update_cache: true
        cache_valid_time: 3600
      when: ansible_os_family == "Debian"

  roles:
    - role: common
      tags: [common]
    - role: nginx
      tags: [nginx, web]
    - role: app
      tags: [app]

  post_tasks:
    - name: Verify services
      ansible.builtin.service:
        name: "{{ item }}"
        state: started
      loop:
        - nginx
      tags: [verify]

  handlers:
    - name: Reload nginx
      ansible.builtin.service:
        name: nginx
        state: reloaded
```

### Role Structure
```yaml
# roles/nginx/tasks/main.yml
---
- name: Include OS-specific variables
  ansible.builtin.include_vars: "{{ ansible_os_family }}.yml"
  tags: [nginx]

- name: Install nginx
  ansible.builtin.package:
    name: nginx
    state: present
  tags: [nginx, install]

- name: Configure nginx
  ansible.builtin.template:
    src: nginx.conf.j2
    dest: /etc/nginx/nginx.conf
    owner: root
    group: root
    mode: '0644'
    validate: nginx -t -c %s
  notify: Reload nginx
  tags: [nginx, config]

- name: Configure virtual hosts
  ansible.builtin.template:
    src: vhost.conf.j2
    dest: "/etc/nginx/sites-available/{{ item.name }}"
    owner: root
    group: root
    mode: '0644'
  loop: "{{ nginx_vhosts }}"
  notify: Reload nginx
  tags: [nginx, vhosts]

- name: Enable virtual hosts
  ansible.builtin.file:
    src: "/etc/nginx/sites-available/{{ item.name }}"
    dest: "/etc/nginx/sites-enabled/{{ item.name }}"
    state: link
  loop: "{{ nginx_vhosts }}"
  notify: Reload nginx
  tags: [nginx, vhosts]

- name: Ensure nginx is started and enabled
  ansible.builtin.service:
    name: nginx
    state: started
    enabled: true
  tags: [nginx]
```

### Inventory Management
```yaml
# inventory/production/hosts.yml
---
all:
  children:
    webservers:
      hosts:
        web1.example.com:
          ansible_host: 10.0.1.10
        web2.example.com:
          ansible_host: 10.0.1.11
      vars:
        http_port: 80
        https_port: 443

    databases:
      hosts:
        db1.example.com:
          ansible_host: 10.0.2.10
          postgresql_primary: true
        db2.example.com:
          ansible_host: 10.0.2.11
          postgresql_primary: false

    loadbalancers:
      hosts:
        lb1.example.com:

  vars:
    ansible_user: deploy
    ansible_ssh_private_key_file: ~/.ssh/deploy_key
    ansible_python_interpreter: /usr/bin/python3
```

### Ansible Vault
```yaml
# Encrypt sensitive variables
# ansible-vault encrypt group_vars/all/vault.yml

# group_vars/all/vault.yml (encrypted)
---
vault_db_password: "supersecret123"
vault_api_key: "sk-xxxxxxxxxxxx"
vault_ssl_certificate: |
  -----BEGIN CERTIFICATE-----
  ...
  -----END CERTIFICATE-----

# Reference in vars.yml
# group_vars/all/vars.yml
---
db_password: "{{ vault_db_password }}"
api_key: "{{ vault_api_key }}"
```

### Dynamic Inventory
```python
#!/usr/bin/env python3
# inventory/aws_ec2.py
"""
Dynamic inventory script for AWS EC2
Usage: ansible-inventory -i aws_ec2.py --list
"""
import boto3
import json

def get_inventory():
    ec2 = boto3.resource('ec2')
    inventory = {
        '_meta': {'hostvars': {}},
        'all': {'children': ['webservers', 'databases']},
        'webservers': {'hosts': []},
        'databases': {'hosts': []},
    }

    for instance in ec2.instances.filter(
        Filters=[{'Name': 'instance-state-name', 'Values': ['running']}]
    ):
        tags = {tag['Key']: tag['Value'] for tag in (instance.tags or [])}
        hostname = tags.get('Name', instance.id)
        role = tags.get('Role', 'unknown')

        if role in inventory:
            inventory[role]['hosts'].append(hostname)

        inventory['_meta']['hostvars'][hostname] = {
            'ansible_host': instance.private_ip_address,
            'ansible_user': 'ubuntu',
            'ec2_instance_id': instance.id,
            'ec2_instance_type': instance.instance_type,
        }

    return inventory

if __name__ == '__main__':
    print(json.dumps(get_inventory(), indent=2))
```

### Testing with Molecule
```yaml
# roles/nginx/molecule/default/molecule.yml
---
dependency:
  name: galaxy

driver:
  name: docker

platforms:
  - name: ubuntu
    image: ubuntu:22.04
    pre_build_image: false
    privileged: true
    command: /lib/systemd/systemd

  - name: debian
    image: debian:12
    pre_build_image: false
    privileged: true

provisioner:
  name: ansible
  inventory:
    group_vars:
      all:
        nginx_vhosts:
          - name: default
            server_name: localhost

verifier:
  name: ansible

# molecule/default/converge.yml
---
- name: Converge
  hosts: all
  become: true
  roles:
    - role: nginx

# molecule/default/verify.yml
---
- name: Verify
  hosts: all
  gather_facts: false
  tasks:
    - name: Check nginx is installed
      ansible.builtin.package:
        name: nginx
        state: present
      check_mode: true
      register: nginx_installed

    - name: Assert nginx is installed
      ansible.builtin.assert:
        that: not nginx_installed.changed

    - name: Check nginx is running
      ansible.builtin.service:
        name: nginx
        state: started
      check_mode: true
      register: nginx_running

    - name: Assert nginx is running
      ansible.builtin.assert:
        that: not nginx_running.changed
```

## Ansible Checklist

```
📋 Ansible Best Practices Checklist

□ STRUCTURE
  □ Roles for reusable code
  □ Separate inventory per environment
  □ group_vars/host_vars for variables
  □ Collection requirements.yml

□ SECURITY
  □ Ansible Vault for secrets
  □ No plaintext passwords
  □ SSH key authentication
  □ Least privilege become

□ QUALITY
  □ YAML linting (yamllint)
  □ Ansible-lint passing
  □ Molecule tests for roles
  □ Idempotent tasks

□ DOCUMENTATION
  □ README for each role
  □ Documented variables
  □ Example playbooks
  □ Tags documented
```

## Warning Triggers

Automatically warn when:

1. **Plaintext secrets**
   > "⚠️ ANSIBLE: Use ansible-vault for sensitive data"

2. **Missing become**
   > "⚠️ ANSIBLE: Specify become explicitly for privileged operations"

3. **Shell/command overuse**
   > "⚠️ ANSIBLE: Use specific modules instead of shell/command when possible"

4. **Missing handlers**
   > "⚠️ ANSIBLE: Use handlers for service restarts instead of inline tasks"
