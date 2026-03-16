# Connect Odoo.sh to Your GitHub Repository

Your code is on GitHub (`Amro-odooerp/Amro--Test`). Follow these steps to connect it to Odoo.sh.

---

## Step 1: Go to Odoo.sh

1. Open **https://www.odoo.sh/**
2. Click **Deploy your platform** (or **Sign in** if you have an account)
3. Sign in with your **GitHub** account
4. Click **Authorize odoo** (twice if prompted)

---

## Step 2: Create or Connect Project

### If you DON'T have an Odoo.sh project yet:

1. Fill in the form:
   - **Github repository:** Select **Existing repository**
   - Choose: **Amro-odooerp / Amro--Test**
   - **Odoo Version:** 19.0 (or your target version)
   - **Subscription Code:** Your Odoo Enterprise code
   - **Hosting location:** Choose your region

2. Click **Deploy**

3. Odoo.sh will create a webhook on your GitHub repo. Pushes to `main` or `Test` will trigger builds.

### If you ALREADY have an Odoo.sh project:

1. Go to your project on Odoo.sh
2. Click **Settings** (gear icon)
3. Check **GitHub key and webhook** section
4. Click **Verify Deploy Key** and **Verify Webhook** to ensure they exist
5. If the project is linked to a **different** repo, you may need to create a new project with the correct repo (repository cannot always be changed)

---

## Step 3: Configure the Branch

1. In Odoo.sh, go to **Branches**
2. Your **Production** branch is usually `main` or `master`
3. **Development** branches: Odoo.sh creates one per Git branch
4. Ensure your branch (`main` or `Test`) exists and is building

---

## Step 4: Addons Path (Important for Custom Modules)

1. Go to **Branches** → **Production** (or your branch)
2. Click **Settings** (branch settings)
3. Find **Addons path** or **Configuration**
4. Add the path to your modules:
   - If modules are in `addons/`: use `addons`
   - If modules are in root (`warehouse_ageing_cost/`): use `.` or add the folder name

---

## Step 5: Verify Connection

1. Push a commit to GitHub (you already did this)
2. In Odoo.sh, go to **Branches** → **Builds**
3. You should see a new build triggered
4. Check build logs for any errors

---

## Troubleshooting

| Problem | Solution |
|---------|----------|
| No builds after push | Verify webhook: Settings → Verify Webhook |
| Module not found | Check addons path in branch settings |
| Build fails | Check build logs for Python/XML errors |
| Repository not in list | Ensure GitHub account has access to Amro-odooerp/Amro--Test |

---

## Odoo.com vs Odoo.sh

- **Odoo.com** (SaaS): Does **NOT** support custom modules. Your URL `amro-odooerp-test-cursor.odoo.com` may be Odoo.com.
- **Odoo.sh**: Supports custom modules. Requires Odoo Enterprise subscription with Odoo.sh.

If you need custom modules, you must use **Odoo.sh**, not Odoo.com.
