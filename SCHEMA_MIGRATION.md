# Schema Migration Strategy

## Overview

Both schemas use `additionalProperties: false` to maintain strict typing. When schema changes are needed, we version them and provide migration utilities.

## Current Versions

- **Candidate CV Schema**: `cvx-1.2.0` (see `schemas/candidate_cv_normalized.json`)
- **Job Description Schema**: `jdx-1.0.0` (see `schemas/job_description_normalized.json`)

## Versioning Convention

Format: `{prefix}-{major}.{minor}.{patch}`

- **Prefix**: `cvx` (Candidate CV) or `jdx` (Job Description)
- **Major**: Breaking changes (removed required fields, changed types)
- **Minor**: Additive changes (new optional fields, new enum values)
- **Patch**: Bug fixes, clarifications

## Migration Strategy

### 1. Breaking Changes (Major Version)

When breaking changes are required:

1. **Create new schema file**: `candidate_cv_normalized_v1.3.0.json`
2. **Update version field** in new schema
3. **Create migration utility** in `migrations/` directory
4. **Keep old schema** for backward compatibility
5. **Update extraction_meta.parser_version** in all new extractions

Example migration:
```typescript
// migrations/migrate_cvx_1.2_to_1.3.ts
export function migrateCVX_1_2_to_1_3(data: CVX_1_2): CVX_1_3 {
  return {
    ...data,
    // Map old fields to new structure
    candidate: {
      ...data.candidate,
      newField: data.candidate.oldField ? transform(data.candidate.oldField) : null
    }
  };
}
```

### 2. Non-Breaking Changes (Minor/Patch)

For additive changes:

1. **Update existing schema** in place
2. **Increment version** (minor for new fields, patch for fixes)
3. **Ensure backward compatibility** - new fields must be optional
4. **Update examples** to show new fields

### 3. Validation

Always validate against schema version:

```typescript
import Ajv from 'ajv';
import cvSchemaV1_2 from './schemas/candidate_cv_normalized.json';
import cvSchemaV1_3 from './schemas/candidate_cv_normalized_v1.3.0.json';

const ajv = new Ajv();
const validateV1_2 = ajv.compile(cvSchemaV1_2);
const validateV1_3 = ajv.compile(cvSchemaV1_3);

function validateAndMigrate(data: unknown): CVX_1_3 {
  // Try current version first
  if (validateV1_3(data)) return data as CVX_1_3;
  
  // Try old version and migrate
  if (validateV1_2(data)) {
    return migrateCVX_1_2_to_1_3(data as CVX_1_2);
  }
  
  throw new Error('Invalid schema version');
}
```

## Best Practices

1. **Never remove required fields** without major version bump
2. **Always make new fields optional** initially
3. **Document breaking changes** in migration utilities
4. **Test migrations** with real data samples
5. **Keep old schemas** for at least 2 major versions
6. **Update extraction_meta.parser_version** in all new extractions

## Version Detection

Check `extraction_meta.parser_version` or `$schema` field to determine schema version:

```typescript
function getSchemaVersion(data: unknown): string {
  if (typeof data === 'object' && data !== null) {
    if ('extraction_meta' in data && 
        typeof (data as any).extraction_meta === 'object' &&
        'parser_version' in (data as any).extraction_meta) {
      return (data as any).extraction_meta.parser_version;
    }
  }
  return 'unknown';
}
```

## Deprecation Policy

- **Deprecate** fields for 1 minor version before removal
- **Log warnings** when deprecated fields are used
- **Provide migration path** in documentation
- **Remove** only in major version bumps

