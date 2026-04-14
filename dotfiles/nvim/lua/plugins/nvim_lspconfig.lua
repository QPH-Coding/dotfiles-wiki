local M = {}

M.server_names = {
  "bashls",
  "lua_ls",
  "pyright",
  "rust_analyzer",
}

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
      local map = function(lhs, rhs, desc)
        vim.keymap.set("n", lhs, rhs, {
          buffer = event.buf,
          desc = desc,
        })
      end

      map("gd", vim.lsp.buf.definition, "Goto definition")
      map("gD", vim.lsp.buf.declaration, "Goto declaration")
      map("gi", vim.lsp.buf.implementation, "Goto implementation")
      map("gr", vim.lsp.buf.references, "Goto references")
      map("K", vim.lsp.buf.hover, "Hover")
      map("<leader>rn", vim.lsp.buf.rename, "Rename symbol")
      map("<leader>ca", vim.lsp.buf.code_action, "Code action")
      map("<leader>e", vim.diagnostic.open_float, "Line diagnostics")
      map("[d", vim.diagnostic.goto_prev, "Previous diagnostic")
      map("]d", vim.diagnostic.goto_next, "Next diagnostic")
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
