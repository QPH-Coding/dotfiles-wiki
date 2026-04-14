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

local map = vim.keymap.set

map("n", "<leader>ff", "<cmd>FzfLua files<CR>", { desc = "Find files" })
map("n", "<leader>fg", "<cmd>FzfLua live_grep<CR>", { desc = "Live grep" })
map("n", "<leader>fb", "<cmd>FzfLua buffers<CR>", { desc = "Buffers" })
map("n", "<leader>fh", "<cmd>FzfLua help_tags<CR>", { desc = "Help tags" })
map("n", "<leader>fo", "<cmd>FzfLua oldfiles<CR>", { desc = "Recent files" })
map("n", "<leader>fr", "<cmd>FzfLua resume<CR>", { desc = "Resume finder" })
