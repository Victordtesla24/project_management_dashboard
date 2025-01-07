Installation Guide
================

Prerequisites
------------
* Python 3.8 or higher
* pip package manager
* Git

Installation Steps
----------------
1. Clone the repository:
   ```bash
   git clone https://github.com/your-org/project-management-dashboard.git
   cd project-management-dashboard
   ```

2. Run the setup script:
   ```bash
   ./scripts/setup.sh
   ```

3. Verify the installation:
   ```bash
   ./scripts/verify_and_fix.sh
   ```

Configuration
------------
The dashboard can be configured by editing the following files:
* `config/dashboard.json` - Dashboard settings
* `config/metrics.json` - Metrics collection settings
* `.env` - Environment variables
