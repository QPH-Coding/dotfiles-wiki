local map = require("core.keymaps").mapper("Core")
local augroup = vim.api.nvim_create_augroup("dotfiles_wiki_core", { clear = true })

map("n", "<Esc>", "<cmd>nohlsearch<CR>", { desc = "Clear search highlight" })
map("n", "<C-h>", "<C-w>h", { desc = "Go to left window" })
map("n", "<C-j>", "<C-w>j", { desc = "Go to lower window" })
map("n", "<C-k>", "<C-w>k", { desc = "Go to upper window" })
map("n", "<C-l>", "<C-w>l", { desc = "Go to right window" })
map({ "n", "v" }, "H", "^", { desc = "Line start" })
map({ "n", "v" }, "L", "$", { desc = "Line end" })

map("n", "<leader>w", "<cmd>write<CR>", { desc = "Write buffer" })
map("n", "<leader>q", "<cmd>quit<CR>", { desc = "Quit window" })
map("n", "<leader>bd", "<cmd>bdelete<CR>", { desc = "Delete buffer" })
map("n", "<leader>yp", function()
  local path = vim.fn.expand("%:p")
  if path == "" then
    vim.notify("Current buffer has no file path", vim.log.levels.WARN)
    return
  end

  vim.fn.setreg('"', path)
  local ok, err = pcall(vim.fn.setreg, "+", path)
  if not ok then
    vim.notify("Failed to copy file path to system clipboard: " .. err, vim.log.levels.ERROR)
    return
  end

  vim.api.nvim_echo({
    { "Copied file path: ", "None" },
    { path, "String" },
  }, false, {})
end, { desc = "Yank file path" })

vim.api.nvim_create_autocmd("TextYankPost", {
  group = augroup,
  desc = "Highlight yanked text",
  callback = function()
    vim.highlight.on_yank()
  end,
})
