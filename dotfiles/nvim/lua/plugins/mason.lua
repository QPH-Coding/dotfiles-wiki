local map = require("core.keymaps").mapper("Mason")

require("mason").setup()

map("n", "<leader>cm", "<cmd>Mason<CR>", { desc = "Mason" })
