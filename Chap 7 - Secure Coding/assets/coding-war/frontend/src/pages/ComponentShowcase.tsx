import { useState } from 'react';
import {
  Button,
  Input,
  Modal,
  Badge,
  Card,
  Table,
  TableHeader,
  TableBody,
  TableRow,
  TableHead,
  TableCell,
  Dropdown,
  DropdownItem,
  Tabs,
  TabsList,
  TabsTrigger,
  TabsContent,
  Skeleton,
  SkeletonText,
  SkeletonCard,
  SkeletonTable,
  SkeletonAvatar,
  ToastContainer,
} from '../components/ui';

/**
 * ComponentShowcase Page
 * 
 * This page demonstrates all base UI components with interactive examples.
 * Requirements: 20.2, 20.3, 20.7, 20.8, 30.1
 */

export default function ComponentShowcase() {
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [inputValue, setInputValue] = useState('');
  const [toasts, setToasts] = useState<Array<{ id: string; type: 'success' | 'error' | 'info' | 'warning'; message: string }>>([]);

  // Sample data for table
  const tableData = [
    { id: 1, name: 'Two Sum', difficulty: 'Easy', acceptance: '85%' },
    { id: 2, name: 'Binary Search', difficulty: 'Medium', acceptance: '60%' },
    { id: 3, name: 'N-Queens', difficulty: 'Hard', acceptance: '35%' },
  ];

  const addToast = (type: 'success' | 'error' | 'info' | 'warning', message: string) => {
    const id = Math.random().toString(36).substr(2, 9);
    setToasts((prev) => [...prev, { id, type, message }]);
  };

  const removeToast = (id: string) => {
    setToasts((prev) => prev.filter((toast) => toast.id !== id));
  };

  return (
    <div className="min-h-screen bg-gray-50 dark:bg-gray-900 py-8">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <header className="mb-8">
          <h1 className="text-4xl font-bold text-gray-900 dark:text-white mb-2">
            UI Component Showcase
          </h1>
          <p className="text-gray-600 dark:text-gray-400">
            Interactive examples of all base UI components with accessibility features
          </p>
        </header>

        <Tabs defaultValue="buttons">
          <TabsList className="mb-8">
            <TabsTrigger value="buttons">Buttons</TabsTrigger>
            <TabsTrigger value="inputs">Inputs</TabsTrigger>
            <TabsTrigger value="modals">Modals</TabsTrigger>
            <TabsTrigger value="tables">Tables</TabsTrigger>
            <TabsTrigger value="badges">Badges</TabsTrigger>
            <TabsTrigger value="cards">Cards</TabsTrigger>
            <TabsTrigger value="dropdowns">Dropdowns</TabsTrigger>
            <TabsTrigger value="tabs">Tabs</TabsTrigger>
            <TabsTrigger value="toasts">Toasts</TabsTrigger>
            <TabsTrigger value="skeletons">Skeletons</TabsTrigger>
          </TabsList>

          {/* Buttons Section */}
          <TabsContent value="buttons">
            <ComponentSection
              title="Button Component"
              description="Buttons with different variants and sizes"
            >
              <div className="space-y-6">
                {/* Button Variants */}
                <div>
                  <h4 className="text-sm font-semibold text-gray-700 dark:text-gray-300 mb-3">
                    Variants
                  </h4>
                  <div className="flex flex-wrap gap-4">
                    <Button variant="primary">Primary</Button>
                    <Button variant="secondary">Secondary</Button>
                    <Button variant="danger">Danger</Button>
                    <Button variant="ghost">Ghost</Button>
                    <Button variant="primary" disabled>Disabled</Button>
                    <Button variant="primary" isLoading>Loading</Button>
                  </div>
                </div>

                {/* Button Sizes */}
                <div>
                  <h4 className="text-sm font-semibold text-gray-700 dark:text-gray-300 mb-3">
                    Sizes
                  </h4>
                  <div className="flex flex-wrap items-center gap-4">
                    <Button size="sm">Small</Button>
                    <Button size="md">Medium</Button>
                    <Button size="lg">Large</Button>
                  </div>
                </div>

                <CodeSnippet code={buttonCode} />
              </div>
            </ComponentSection>
          </TabsContent>

          {/* Inputs Section */}
          <TabsContent value="inputs">
            <ComponentSection
              title="Input Component"
              description="Input fields with different states"
            >
              <div className="space-y-6 max-w-md">
                <Input
                  label="Default Input"
                  placeholder="Enter text..."
                  value={inputValue}
                  onChange={(e) => setInputValue(e.target.value)}
                />

                <Input
                  label="Error State"
                  placeholder="Invalid input"
                  error="This field is required"
                />

                <Input
                  label="Success State"
                  value="Valid input"
                  success="Input is valid"
                  readOnly
                />

                <Input
                  label="Disabled Input"
                  placeholder="Disabled"
                  disabled
                />

                <Input
                  label="With Helper Text"
                  placeholder="Enter your email"
                  helperText="We'll never share your email"
                />

                <CodeSnippet code={inputCode} />
              </div>
            </ComponentSection>
          </TabsContent>

          {/* Modals Section */}
          <TabsContent value="modals">
            <ComponentSection
              title="Modal Component"
              description="Modal dialogs with focus trap and keyboard navigation"
            >
              <div className="space-y-4">
                <Button onClick={() => setIsModalOpen(true)}>
                  Open Modal
                </Button>

                <Modal
                  isOpen={isModalOpen}
                  onClose={() => setIsModalOpen(false)}
                  title="Example Modal"
                  footer={
                    <>
                      <Button variant="secondary" onClick={() => setIsModalOpen(false)}>
                        Cancel
                      </Button>
                      <Button onClick={() => setIsModalOpen(false)} className="ml-3">
                        Confirm
                      </Button>
                    </>
                  }
                >
                  <p className="text-gray-600 dark:text-gray-400">
                    This is a modal dialog with focus trap. Press ESC to close or click outside.
                    Try tabbing through the buttons to see the focus trap in action.
                  </p>
                </Modal>

                <CodeSnippet code={modalCode} />
              </div>
            </ComponentSection>
          </TabsContent>

          {/* Tables Section */}
          <TabsContent value="tables">
            <ComponentSection
              title="Table Component"
              description="Responsive tables with sorting capability"
            >
              <Table>
                <TableHeader>
                  <TableRow>
                    <TableHead sortable>ID</TableHead>
                    <TableHead sortable>Name</TableHead>
                    <TableHead sortable>Difficulty</TableHead>
                    <TableHead sortable>Acceptance</TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {tableData.map((row) => (
                    <TableRow key={row.id} onClick={() => alert(`Clicked ${row.name}`)}>
                      <TableCell>{row.id}</TableCell>
                      <TableCell>{row.name}</TableCell>
                      <TableCell>
                        <Badge variant={row.difficulty.toLowerCase() as 'easy' | 'medium' | 'hard'}>
                          {row.difficulty}
                        </Badge>
                      </TableCell>
                      <TableCell>{row.acceptance}</TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
              <CodeSnippet code={tableCode} />
            </ComponentSection>
          </TabsContent>

          {/* Badges Section */}
          <TabsContent value="badges">
            <ComponentSection
              title="Badge Component"
              description="Status indicators with different colors"
            >
              <div className="space-y-6">
                <div>
                  <h4 className="text-sm font-semibold text-gray-700 dark:text-gray-300 mb-3">
                    Status Badges
                  </h4>
                  <div className="flex flex-wrap gap-3">
                    <Badge variant="success">Accepted</Badge>
                    <Badge variant="error">Wrong Answer</Badge>
                    <Badge variant="warning">Pending</Badge>
                    <Badge variant="info">Running</Badge>
                    <Badge variant="gray">Queued</Badge>
                  </div>
                </div>

                <div>
                  <h4 className="text-sm font-semibold text-gray-700 dark:text-gray-300 mb-3">
                    Difficulty Badges
                  </h4>
                  <div className="flex flex-wrap gap-3">
                    <Badge variant="easy">Easy</Badge>
                    <Badge variant="medium">Medium</Badge>
                    <Badge variant="hard">Hard</Badge>
                  </div>
                </div>

                <div>
                  <h4 className="text-sm font-semibold text-gray-700 dark:text-gray-300 mb-3">
                    Badge Sizes
                  </h4>
                  <div className="flex flex-wrap items-center gap-3">
                    <Badge size="sm">Small</Badge>
                    <Badge size="md">Medium</Badge>
                    <Badge size="lg">Large</Badge>
                  </div>
                </div>

                <CodeSnippet code={badgeCode} />
              </div>
            </ComponentSection>
          </TabsContent>

          {/* Cards Section */}
          <TabsContent value="cards">
            <ComponentSection
              title="Card Component"
              description="Content containers with various layouts"
            >
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                <Card>
                  <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-2">
                    Simple Card
                  </h3>
                  <p className="text-gray-600 dark:text-gray-400">
                    A basic card with title and description.
                  </p>
                </Card>

                <Card hover>
                  <div className="flex items-center justify-between mb-2">
                    <h3 className="text-lg font-semibold text-gray-900 dark:text-white">
                      Problem Card
                    </h3>
                    <Badge variant="easy">Easy</Badge>
                  </div>
                  <p className="text-gray-600 dark:text-gray-400 mb-4">
                    Two Sum - Find two numbers that add up to target.
                  </p>
                  <div className="text-sm text-gray-500 dark:text-gray-400">
                    Acceptance: 85%
                  </div>
                </Card>

                <Card>
                  <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-2">
                    Contest Card
                  </h3>
                  <p className="text-gray-600 dark:text-gray-400 mb-4">
                    Weekly Contest #42
                  </p>
                  <Button className="w-full">Register</Button>
                </Card>
              </div>
              <CodeSnippet code={cardCode} />
            </ComponentSection>
          </TabsContent>

          {/* Dropdowns Section */}
          <TabsContent value="dropdowns">
            <ComponentSection
              title="Dropdown Component"
              description="Dropdown menus with keyboard navigation"
            >
              <div className="flex gap-4">
                <Dropdown
                  trigger={
                    <Button variant="secondary">
                      Options
                      <svg className="-mr-1 ml-2 h-5 w-5" fill="currentColor" viewBox="0 0 20 20">
                        <path fillRule="evenodd" d="M5.293 7.293a1 1 0 011.414 0L10 10.586l3.293-3.293a1 1 0 111.414 1.414l-4 4a1 1 0 01-1.414 0l-4-4a1 1 0 010-1.414z" clipRule="evenodd" />
                      </svg>
                    </Button>
                  }
                >
                  <DropdownItem onClick={() => alert('Edit clicked')}>Edit</DropdownItem>
                  <DropdownItem onClick={() => alert('Duplicate clicked')}>Duplicate</DropdownItem>
                  <DropdownItem onClick={() => alert('Delete clicked')} danger>Delete</DropdownItem>
                </Dropdown>

                <Dropdown
                  align="left"
                  trigger={
                    <Button variant="secondary">Left Aligned</Button>
                  }
                >
                  <DropdownItem>Option 1</DropdownItem>
                  <DropdownItem>Option 2</DropdownItem>
                  <DropdownItem>Option 3</DropdownItem>
                </Dropdown>
              </div>
              <CodeSnippet code={dropdownCode} />
            </ComponentSection>
          </TabsContent>

          {/* Tabs Section */}
          <TabsContent value="tabs">
            <ComponentSection
              title="Tabs Component"
              description="Tabbed interfaces for organizing content"
            >
              <Tabs defaultValue="tab1">
                <TabsList>
                  <TabsTrigger value="tab1">Tab 1</TabsTrigger>
                  <TabsTrigger value="tab2">Tab 2</TabsTrigger>
                  <TabsTrigger value="tab3">Tab 3</TabsTrigger>
                </TabsList>
                <TabsContent value="tab1">
                  <Card>
                    <p className="text-gray-700 dark:text-gray-300">
                      This is the content for Tab 1. You can put any content here.
                    </p>
                  </Card>
                </TabsContent>
                <TabsContent value="tab2">
                  <Card>
                    <p className="text-gray-700 dark:text-gray-300">
                      This is the content for Tab 2. Tabs are great for organizing related content.
                    </p>
                  </Card>
                </TabsContent>
                <TabsContent value="tab3">
                  <Card>
                    <p className="text-gray-700 dark:text-gray-300">
                      This is the content for Tab 3. Try navigating with keyboard!
                    </p>
                  </Card>
                </TabsContent>
              </Tabs>
              <CodeSnippet code={tabsCode} />
            </ComponentSection>
          </TabsContent>

          {/* Toasts Section */}
          <TabsContent value="toasts">
            <ComponentSection
              title="Toast Notifications"
              description="Temporary notifications with auto-dismiss"
            >
              <div className="space-y-4">
                <div className="flex flex-wrap gap-4">
                  <Button
                    variant="primary"
                    onClick={() => addToast('success', 'Success! Your changes have been saved.')}
                  >
                    Show Success
                  </Button>
                  <Button
                    onClick={() => addToast('error', 'Error! Something went wrong.')}
                  >
                    Show Error
                  </Button>
                  <Button
                    onClick={() => addToast('info', 'Info: New features are available.')}
                  >
                    Show Info
                  </Button>
                  <Button
                    onClick={() => addToast('warning', 'Warning: Your session will expire soon.')}
                  >
                    Show Warning
                  </Button>
                </div>
                <p className="text-sm text-gray-600 dark:text-gray-400">
                  Click the buttons above to see toast notifications. They will auto-dismiss after 5 seconds.
                </p>
              </div>
              <CodeSnippet code={toastCode} />
            </ComponentSection>
          </TabsContent>

          {/* Skeletons Section */}
          <TabsContent value="skeletons">
            <ComponentSection
              title="Skeleton Loading States"
              description="Loading placeholders for different content types"
            >
              <div className="space-y-8">
                <div>
                  <h4 className="text-sm font-semibold text-gray-700 dark:text-gray-300 mb-3">
                    Text Content
                  </h4>
                  <SkeletonText lines={3} />
                </div>

                <div>
                  <h4 className="text-sm font-semibold text-gray-700 dark:text-gray-300 mb-3">
                    Card Content
                  </h4>
                  <SkeletonCard />
                </div>

                <div>
                  <h4 className="text-sm font-semibold text-gray-700 dark:text-gray-300 mb-3">
                    Table Content
                  </h4>
                  <SkeletonTable rows={3} />
                </div>

                <div>
                  <h4 className="text-sm font-semibold text-gray-700 dark:text-gray-300 mb-3">
                    User Profile
                  </h4>
                  <SkeletonAvatar />
                </div>

                <div>
                  <h4 className="text-sm font-semibold text-gray-700 dark:text-gray-300 mb-3">
                    Custom Skeletons
                  </h4>
                  <div className="space-y-3">
                    <Skeleton width="100%" height="20px" />
                    <Skeleton width="75%" height="20px" />
                    <Skeleton variant="circular" width="60px" height="60px" />
                    <Skeleton variant="rectangular" width="200px" height="100px" />
                  </div>
                </div>
              </div>
              <CodeSnippet code={skeletonCode} />
            </ComponentSection>
          </TabsContent>
        </Tabs>

        {/* Accessibility Testing Section */}
        <div className="mt-12 p-6 bg-blue-50 dark:bg-blue-900/20 border border-blue-200 dark:border-blue-800 rounded-lg">
          <h2 className="text-xl font-semibold text-blue-900 dark:text-blue-200 mb-4">
            Accessibility Features
          </h2>
          <ul className="space-y-2 text-blue-800 dark:text-blue-300">
            <li>✓ Keyboard navigation support (Tab, Enter, Escape, Arrow keys)</li>
            <li>✓ Focus indicators visible on all interactive elements</li>
            <li>✓ ARIA labels and roles for screen readers</li>
            <li>✓ Color contrast meets WCAG 2.1 Level AA (4.5:1 for text)</li>
            <li>✓ Semantic HTML elements for better accessibility</li>
            <li>✓ Focus trap in modals</li>
            <li>✓ Descriptive error messages linked to inputs</li>
          </ul>
        </div>
      </div>

      {/* Toast Container */}
      <ToastContainer toasts={toasts} onClose={removeToast} />
    </div>
  );
}

// Helper Components

interface ComponentSectionProps {
  title: string;
  description: string;
  children: React.ReactNode;
}

function ComponentSection({ title, description, children }: ComponentSectionProps) {
  return (
    <section className="bg-white dark:bg-gray-800 rounded-lg shadow-md p-6">
      <h2 className="text-2xl font-bold text-gray-900 dark:text-white mb-2">
        {title}
      </h2>
      <p className="text-gray-600 dark:text-gray-400 mb-6">
        {description}
      </p>
      {children}
    </section>
  );
}

interface CodeSnippetProps {
  code: string;
}

function CodeSnippet({ code }: CodeSnippetProps) {
  return (
    <div className="mt-6">
      <h4 className="text-sm font-semibold text-gray-700 dark:text-gray-300 mb-2">
        Code Example
      </h4>
      <pre className="bg-gray-900 text-gray-100 p-4 rounded-md overflow-x-auto text-sm">
        <code>{code}</code>
      </pre>
    </div>
  );
}

// Code Snippets for Examples

const buttonCode = `import { Button } from '@/components/ui';

// Button variants
<Button variant="primary">Primary</Button>
<Button variant="secondary">Secondary</Button>
<Button variant="danger">Danger</Button>
<Button variant="ghost">Ghost</Button>

// Button sizes
<Button size="sm">Small</Button>
<Button size="md">Medium</Button>
<Button size="lg">Large</Button>

// Button states
<Button disabled>Disabled</Button>
<Button isLoading>Loading</Button>`;

const inputCode = `import { Input } from '@/components/ui';

// Basic input
<Input
  label="Username"
  placeholder="Enter username"
  value={value}
  onChange={(e) => setValue(e.target.value)}
/>

// Input with error
<Input
  label="Email"
  error="This field is required"
/>

// Input with success
<Input
  label="Password"
  success="Password is strong"
/>

// Disabled input
<Input
  label="Disabled"
  disabled
/>`;

const modalCode = `import { Modal, Button } from '@/components/ui';

const [isOpen, setIsOpen] = useState(false);

<Button onClick={() => setIsOpen(true)}>
  Open Modal
</Button>

<Modal
  isOpen={isOpen}
  onClose={() => setIsOpen(false)}
  title="Modal Title"
  footer={
    <>
      <Button variant="secondary" onClick={() => setIsOpen(false)}>
        Cancel
      </Button>
      <Button onClick={() => setIsOpen(false)}>
        Confirm
      </Button>
    </>
  }
>
  <p>Modal content goes here...</p>
</Modal>`;

const tableCode = `import { Table, TableHeader, TableBody, TableRow, TableHead, TableCell } from '@/components/ui';

<Table>
  <TableHeader>
    <TableRow>
      <TableHead sortable>Name</TableHead>
      <TableHead sortable>Status</TableHead>
    </TableRow>
  </TableHeader>
  <TableBody>
    <TableRow onClick={() => handleClick()}>
      <TableCell>Problem A</TableCell>
      <TableCell>Accepted</TableCell>
    </TableRow>
  </TableBody>
</Table>`;

const badgeCode = `import { Badge } from '@/components/ui';

// Status badges
<Badge variant="success">Accepted</Badge>
<Badge variant="error">Wrong Answer</Badge>
<Badge variant="warning">Pending</Badge>

// Difficulty badges
<Badge variant="easy">Easy</Badge>
<Badge variant="medium">Medium</Badge>
<Badge variant="hard">Hard</Badge>

// Badge sizes
<Badge size="sm">Small</Badge>
<Badge size="md">Medium</Badge>
<Badge size="lg">Large</Badge>`;

const cardCode = `import { Card, Badge, Button } from '@/components/ui';

<Card>
  <h3>Card Title</h3>
  <p>Card description...</p>
</Card>

<Card hover>
  <div className="flex justify-between">
    <h3>Problem Card</h3>
    <Badge variant="easy">Easy</Badge>
  </div>
  <p>Problem description...</p>
  <Button>Solve</Button>
</Card>`;

const dropdownCode = `import { Dropdown, DropdownItem, Button } from '@/components/ui';

<Dropdown
  trigger={<Button>Options</Button>}
  align="right"
>
  <DropdownItem onClick={() => handleEdit()}>
    Edit
  </DropdownItem>
  <DropdownItem onClick={() => handleDuplicate()}>
    Duplicate
  </DropdownItem>
  <DropdownItem onClick={() => handleDelete()} danger>
    Delete
  </DropdownItem>
</Dropdown>`;

const tabsCode = `import { Tabs, TabsList, TabsTrigger, TabsContent } from '@/components/ui';

<Tabs defaultValue="tab1">
  <TabsList>
    <TabsTrigger value="tab1">Tab 1</TabsTrigger>
    <TabsTrigger value="tab2">Tab 2</TabsTrigger>
    <TabsTrigger value="tab3">Tab 3</TabsTrigger>
  </TabsList>
  
  <TabsContent value="tab1">
    Content for Tab 1
  </TabsContent>
  
  <TabsContent value="tab2">
    Content for Tab 2
  </TabsContent>
  
  <TabsContent value="tab3">
    Content for Tab 3
  </TabsContent>
</Tabs>`;

const toastCode = `import { ToastContainer } from '@/components/ui';
import { useState } from 'react';

const [toasts, setToasts] = useState([]);

const addToast = (type, message) => {
  const id = Math.random().toString(36).substr(2, 9);
  setToasts(prev => [...prev, { id, type, message }]);
};

const removeToast = (id) => {
  setToasts(prev => prev.filter(toast => toast.id !== id));
};

// Show toast
addToast('success', 'Operation successful!');
addToast('error', 'Something went wrong!');
addToast('info', 'New update available');
addToast('warning', 'Session expiring soon');

// Render container
<ToastContainer toasts={toasts} onClose={removeToast} />`;

const skeletonCode = `import { Skeleton, SkeletonText, SkeletonCard, SkeletonTable, SkeletonAvatar } from '@/components/ui';

// Preset skeletons
<SkeletonText lines={3} />
<SkeletonCard />
<SkeletonTable rows={5} />
<SkeletonAvatar />

// Custom skeletons
<Skeleton width="100%" height="20px" />
<Skeleton variant="circular" width="60px" height="60px" />
<Skeleton variant="rectangular" width="200px" height="100px" />`;
