local M = {}
local keymaps = require("core.keymaps")

M.server_names = {
  "bashls",
  "lua_ls",
  "pyright",
  "rust_analyzer",
}

local lsp_keymaps = {
  { lhs = "gd", rhs = vim.lsp.buf.definition, desc = "Goto definition" },
  { lhs = "gD", rhs = vim.lsp.buf.declaration, desc = "Goto declaration" },
  { lhs = "gi", rhs = vim.lsp.buf.implementation, desc = "Goto implementation" },
  { lhs = "gr", rhs = vim.lsp.buf.references, desc = "Goto references" },
  { lhs = "K", rhs = vim.lsp.buf.hover, desc = "Hover" },
  { lhs = "<leader>rn", rhs = vim.lsp.buf.rename, desc = "Rename symbol" },
  { lhs = "<leader>ca", rhs = vim.lsp.buf.code_action, desc = "Code action" },
  { lhs = "<leader>e", rhs = vim.diagnostic.open_float, desc = "Line diagnostics" },
  { lhs = "[d", rhs = vim.diagnostic.goto_prev, desc = "Previous diagnostic" },
  { lhs = "]d", rhs = vim.diagnostic.goto_next, desc = "Next diagnostic" },
}

keymaps.register("LSP", vim.tbl_map(function(mapping)
  return {
    mode = "n",
    lhs = mapping.lhs,
    desc = mapping.desc,
    scope = "buffer-local",
  }
end, lsp_keymaps))

function M.setup(capabilities)
  vim.diagnostic.config({
    severity_sort = true,
    underline = true,
    update_in_insert = false,
    virtual_text = {
      spacing = 2,
      source = "if_many",
    },
    float = {
      border = "rounded",
      source = "if_many",
    },
  })

  local augroup = vim.api.nvim_create_augroup("dotfiles_wiki_lsp", { clear = true })

  vim.api.nvim_create_autocmd("LspAttach", {
    group = augroup,
    desc = "LSP buffer-local keymaps",
    callback = function(event)
      local buffer_map = keymaps.buffer_mapper("LSP", event.buf)

      for _, mapping in ipairs(lsp_keymaps) do
        buffer_map("n", mapping.lhs, mapping.rhs, {
          desc = mapping.desc,
        })
      end
    end,
  })

  local servers = {
    bashls = {},
    lua_ls = {
      settings = {
        Lua = {},
      },
      on_init = function(client)
        if client.workspace_folders then
          local path = client.workspace_folders[1].name
          if
            path ~= vim.fn.stdpath("config")
            and (vim.uv.fs_stat(path .. "/.luarc.json") or vim.uv.fs_stat(path .. "/.luarc.jsonc"))
          then
            return
          end
        end

        client.config.settings.Lua = vim.tbl_deep_extend("force", client.config.settings.Lua, {
          runtime = {
            version = "LuaJIT",
            path = {
              "lua/?.lua",
              "lua/?/init.lua",
            },
          },
          workspace = {
            checkThirdParty = false,
            library = {
              vim.env.VIMRUNTIME,
            },
          },
        })
      end,
    },
    pyright = {},
    rust_analyzer = {},
  }

  for name, config in pairs(servers) do
    local server_config = vim.deepcopy(config)
    server_config.capabilities = vim.tbl_deep_extend(
      "force",
      {},
      capabilities or {},
      server_config.capabilities or {}
    )

    vim.lsp.config(name, server_config)
  end
end

return M
