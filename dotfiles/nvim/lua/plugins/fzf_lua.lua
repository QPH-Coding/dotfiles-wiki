local keymaps = require("core.keymaps")
local map = keymaps.mapper("FzfLua")
local cheatsheet = keymaps.mapper("Cheatsheet")

require("fzf-lua").setup({
  defaults = {
    file_icons = false,
  },
  files = {
    cwd_prompt = false,
  },
  grep = {
    prompt = "Rg> ",
  },
})

map("n", "<leader>ff", "<cmd>FzfLua files<CR>", { desc = "Find files" })
map("n", "<leader>fg", "<cmd>FzfLua live_grep<CR>", { desc = "Live grep" })
map("n", "<leader>fb", "<cmd>FzfLua buffers<CR>", { desc = "Buffers" })
map("n", "<leader>/", "<cmd>FzfLua blines<CR>", { desc = "Buffer lines" })
map("n", "<leader>ds", "<cmd>FzfLua lgrep_curbuf<CR>", { desc = "Live grep current buffer" })
map("n", "<leader>fh", "<cmd>FzfLua help_tags<CR>", { desc = "Help tags" })
map("n", "<leader>fo", "<cmd>FzfLua oldfiles<CR>", { desc = "Recent files" })
map("n", "<leader>fr", "<cmd>FzfLua resume<CR>", { desc = "Resume finder" })
cheatsheet("n", "<leader>fk", "<cmd>CheatsheetSearch<CR>", { desc = "Search keymaps" })
cheatsheet("n", "<leader>fK", "<cmd>Cheatsheet<CR>", { desc = "Keymap cheatsheet" })
