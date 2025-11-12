# @senda/ui

Shared UI components for Senda platform.

## Components

- `Button`: Reusable button component with variants
- `Card`: Card component for content containers

## Usage

```tsx
import { Button, Card } from '@senda/ui';

function MyComponent() {
  return (
    <Card title="Example">
      <Button variant="primary" onClick={() => console.log('clicked')}>
        Click me
      </Button>
    </Card>
  );
}
```
