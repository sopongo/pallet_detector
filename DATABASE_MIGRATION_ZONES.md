# Database Migration - Zone Detection System

## Overview
This migration adds zone support to the pallet detection system, allowing each pallet to be associated with a specific zone and have zone-specific alert thresholds.

## Migration SQL

Execute the following SQL commands on your database:

```sql
-- Add zone columns to tb_pallet table
ALTER TABLE tb_pallet 
ADD COLUMN zone_id INT DEFAULT NULL COMMENT 'Zone ID where pallet is located' AFTER detector_count,
ADD COLUMN zone_name VARCHAR(100) DEFAULT NULL COMMENT 'Zone name' AFTER zone_id,
ADD COLUMN zone_threshold INT DEFAULT NULL COMMENT 'Alert threshold (minutes) for this zone' AFTER zone_name;

-- Add indexes for better query performance
CREATE INDEX idx_zone ON tb_pallet(zone_id);
CREATE INDEX idx_zone_status ON tb_pallet(zone_id, status);

-- Verify columns were added
DESCRIBE tb_pallet;
```

## Verification

After running the migration, verify the changes:

```sql
-- Check if columns exist
SHOW COLUMNS FROM tb_pallet LIKE 'zone%';

-- Expected output:
-- zone_id       | int(11)      | YES  |     | NULL    |
-- zone_name     | varchar(100) | YES  |     | NULL    |
-- zone_threshold| int(11)      | YES  |     | NULL    |

-- Check if indexes were created
SHOW INDEX FROM tb_pallet WHERE Key_name LIKE 'idx_zone%';

-- Expected output:
-- idx_zone
-- idx_zone_status
```

## Rollback (if needed)

If you need to revert this migration:

```sql
-- Remove indexes
DROP INDEX idx_zone ON tb_pallet;
DROP INDEX idx_zone_status ON tb_pallet;

-- Remove columns
ALTER TABLE tb_pallet 
DROP COLUMN zone_id,
DROP COLUMN zone_name,
DROP COLUMN zone_threshold;
```

## Notes

1. **Existing Data**: Existing pallets will have NULL values for zone columns. This is expected behavior.
2. **Backward Compatibility**: The system works without zones (falls back to global detection and threshold).
3. **Zone Threshold**: If zone_threshold is NULL, the system uses the global alert threshold from config.
4. **Performance**: The indexes ensure efficient queries when filtering by zone or zone+status.

## Testing After Migration

1. Verify columns exist:
   ```bash
   mysql -u your_user -p your_database -e "DESCRIBE tb_pallet;"
   ```

2. Test zone assignment:
   - Draw zones in the Zone Configuration tab
   - Enable zone system
   - Run detection service
   - Check if new pallets have zone_id, zone_name, zone_threshold populated

3. Test zone-specific thresholds:
   - Set different thresholds for different zones (e.g., Zone A: 30 min, Zone B: 10 min)
   - Place pallet in Zone B
   - Wait 11 minutes
   - Verify alert is triggered for Zone B but not Zone A

## Migration Checklist

- [ ] Backup database before migration
- [ ] Execute SQL migration commands
- [ ] Verify columns were added correctly
- [ ] Verify indexes were created
- [ ] Test pallet creation with zones
- [ ] Test zone-specific alert thresholds
- [ ] Update any custom queries/reports that reference tb_pallet
