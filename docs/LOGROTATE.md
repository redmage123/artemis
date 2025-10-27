# Artemis Logrotate Configuration

## Overview

Artemis generates logs from multiple sources:
- **Main logs**: `/var/log/artemis/*.log` - Primary application logs
- **Fallback logs**: `/tmp/artemis_logs/*.log` - When /var/log/artemis is not writable
- **Upload logs**: `/tmp/*_upload*.log` - Book/course upload scripts
- **RAG logs**: `.artemis_data/logs/*.log` - RAG database operations

Without log rotation, these can grow indefinitely and fill up disk space.

## Quick Setup

```bash
cd /home/bbrelin/src/repos/artemis
./scripts/setup_logrotate.sh
```

This script will:
1. Create `/var/log/artemis` directory
2. Fix permissions so your user can write logs
3. Install logrotate configuration to `/etc/logrotate.d/artemis`
4. Verify the configuration

## Manual Installation

If you prefer to install manually:

```bash
# 1. Create log directory and fix permissions
sudo mkdir -p /var/log/artemis
sudo chown -R $USER:$USER /var/log/artemis
sudo chmod 755 /var/log/artemis

# 2. Install logrotate config
sudo cp logrotate.d/artemis /etc/logrotate.d/artemis
sudo chmod 644 /etc/logrotate.d/artemis
sudo chown root:root /etc/logrotate.d/artemis

# 3. Verify configuration
sudo logrotate -d /etc/logrotate.d/artemis
```

## Rotation Schedule

### Main Logs (`/var/log/artemis/*.log`)
- **Frequency**: Daily
- **Retention**: 30 days
- **Max size**: 100MB per file
- **Compression**: Yes (delayed by 1 rotation)
- **Format**: `artemis.log-20251027.gz`

### Temp Logs (`/tmp/artemis_logs/*.log`)
- **Frequency**: Daily
- **Retention**: 7 days
- **Max size**: 50MB per file
- **Compression**: Yes
- **Auto-cleanup**: Files older than 7 days deleted

### Upload Logs (`/tmp/*_upload*.log`)
- **Frequency**: Weekly
- **Retention**: 4 weeks
- **Max size**: 10MB per file
- **Compression**: Yes
- **Auto-cleanup**: Files older than 30 days deleted

## Testing

### Dry Run (see what would happen)
```bash
sudo logrotate -d /etc/logrotate.d/artemis
```

### Force Rotation (useful for testing)
```bash
sudo logrotate -f /etc/logrotate.d/artemis
```

### Check Status
```bash
cat /var/lib/logrotate/status | grep artemis
```

### View Rotated Logs
```bash
# List rotated logs
ls -lh /var/log/artemis/

# View compressed log
zcat /var/log/artemis/artemis.log-20251027.gz | less

# View recent uncompressed backup
cat /var/log/artemis/artemis.log-20251027
```

## Troubleshooting

### Logs Not Rotating

**Check if logrotate is running:**
```bash
sudo systemctl status logrotate.timer  # systemd timer
# OR
crontab -l | grep logrotate  # cron job
```

**Check logrotate configuration:**
```bash
sudo logrotate -d /etc/logrotate.d/artemis
```

**Force a rotation to test:**
```bash
sudo logrotate -f /etc/logrotate.d/artemis
```

### Permission Denied Errors

**Fix /var/log/artemis permissions:**
```bash
sudo chown -R $USER:$USER /var/log/artemis
sudo chmod 755 /var/log/artemis
```

**Update logrotate config `create` directive:**
Edit `/etc/logrotate.d/artemis` and change:
```
create 0644 bbrelin bbrelin
```
to match your username.

### Disk Space Issues

**Find largest log files:**
```bash
du -h /var/log/artemis/* | sort -rh | head -10
du -h /tmp/artemis_logs/* | sort -rh | head -10
```

**Manually compress old logs:**
```bash
cd /var/log/artemis
gzip artemis.log-*
```

**Delete very old logs:**
```bash
find /var/log/artemis -name "*.log-*.gz" -mtime +60 -delete
```

## Integration with ArtemisLogger

The `ArtemisLogger` class automatically:
1. Tries to write to `/var/log/artemis/`
2. Falls back to `/tmp/artemis_logs/` if permission denied
3. Creates log files with timestamps in the name
4. Logs are compatible with logrotate wildcards

To ensure logs are written to the correct location:
```python
from artemis_logger import ArtemisLogger

# Logger will use /var/log/artemis if available
logger = ArtemisLogger()
logger.log("Test message", "INFO")
```

## Customization

Edit `/etc/logrotate.d/artemis` to customize:

**Change retention period:**
```
rotate 60  # Keep 60 days instead of 30
```

**Change rotation frequency:**
```
weekly  # Rotate weekly instead of daily
```

**Change size threshold:**
```
size 500M  # Rotate when log exceeds 500MB
```

**Disable compression:**
```
nocompress  # Don't compress old logs
```

After editing, verify:
```bash
sudo logrotate -d /etc/logrotate.d/artemis
```

## Monitoring

### Set up log size monitoring (optional)

Create a cron job to alert on large logs:
```bash
# Add to crontab: crontab -e
0 2 * * * /home/bbrelin/src/repos/artemis/scripts/check_log_sizes.sh
```

Create monitoring script:
```bash
#!/bin/bash
# scripts/check_log_sizes.sh

MAX_SIZE_MB=500
ALERT_EMAIL="your@email.com"

for log in /var/log/artemis/*.log /tmp/artemis_logs/*.log; do
    if [ -f "$log" ]; then
        size_mb=$(du -m "$log" | cut -f1)
        if [ $size_mb -gt $MAX_SIZE_MB ]; then
            echo "WARNING: $log is ${size_mb}MB (exceeds ${MAX_SIZE_MB}MB)" | \
                mail -s "Artemis Log Alert" $ALERT_EMAIL
        fi
    fi
done
```

## See Also

- [Logrotate Man Page](https://linux.die.net/man/8/logrotate)
- [ArtemisLogger Documentation](../src/artemis_logger.py)
- [Artemis Configuration Guide](./CONFIGURATION.md)
