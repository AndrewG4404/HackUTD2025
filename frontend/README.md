# VendorLens Frontend

Next.js 14 frontend application for VendorLens.

## Setup

1. Install dependencies:
```bash
npm install
```

2. Create `.env.local` file (optional, defaults to `http://localhost:8000/api`):
```bash
NEXT_PUBLIC_API_URL=http://localhost:8000/api
```

3. Run development server:
```bash
npm run dev
```

Frontend will run on `http://localhost:3000`

## Project Structure

- `app/` - Next.js 14 app directory
  - `page.tsx` - Landing page
  - `apply/` - Vendor application form
  - `assess/` - Assessment setup form
  - `evaluations/[id]/` - Results page
- `lib/` - Utilities and API client
  - `api.ts` - Centralized API calls

## Pages

1. **`/`** - Landing page with workflow selection
2. **`/apply`** - Vendor application form
3. **`/assess`** - Vendor assessment setup form
4. **`/evaluations/[id]`** - Evaluation results page with polling

## Development Notes

- Uses TypeScript for type safety
- Tailwind CSS for styling
- Axios for API calls
- Recharts for data visualization (radar charts, etc.)
- API client is centralized in `lib/api.ts`

