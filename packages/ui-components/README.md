# UI Components Package

Shared React component library for BrainSAIT SSDP platform.

## Features

- Reusable UI components
- TypeScript support
- Tailwind CSS styling
- Storybook documentation
- Arabic/English RTL support
- Accessible (WCAG 2.1 AA)

## Components

### Layout
- `Container` - Responsive container
- `Grid` - Flexible grid system
- `Stack` - Vertical/horizontal stack
- `Divider` - Visual separator

### Forms
- `Input` - Text input with validation
- `Select` - Dropdown select
- `Checkbox` - Checkbox input
- `Radio` - Radio button
- `Switch` - Toggle switch
- `DatePicker` - Date selection

### Buttons
- `Button` - Primary button
- `IconButton` - Icon-only button
- `ButtonGroup` - Button group

### Data Display
- `Table` - Data table
- `Card` - Content card
- `Badge` - Status badge
- `Tag` - Label tag
- `Avatar` - User avatar

### Feedback
- `Alert` - Alert messages
- `Toast` - Toast notifications
- `Modal` - Modal dialogs
- `Spinner` - Loading spinner

### Navigation
- `Tabs` - Tab navigation
- `Breadcrumbs` - Breadcrumb navigation
- `Menu` - Dropdown menu

## Usage

```tsx
import { Button, Card } from '@brainsait/ui-components';

function MyComponent() {
  return (
    <Card>
      <Button variant="primary">Click Me</Button>
    </Card>
  );
}
```

## Development

```bash
npm install
npm run dev

# Run Storybook
npm run storybook
```

## Testing

```bash
npm test
```
